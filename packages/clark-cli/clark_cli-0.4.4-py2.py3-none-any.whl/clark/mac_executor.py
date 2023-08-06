import pathlib
import os
import re
import datetime
import subprocess
import time
from typing import List

import click
from colorama import Fore

from clark.execution import ExecutionExtraction, ScriptInputOutput, Script
from clark.executor import ScriptExecutor


OPEN_REGEX = re.compile(r'(open|open_nocancel)\("(.*?)[\\]*\d*", .*, .*\)\s*=\s*(\-?\d+)', re.IGNORECASE)
CLOSE_REGEX = re.compile(r"(close|close_nocancel)\((.*?)\)", re.IGNORECASE)
OPEN_DIR_REGEX = re.compile(r'open_nocancel\(".*", 0x110000', re.IGNORECASE)

OPEN = 'open'
CLOSE = 'close'


class MacScriptExecutor(ScriptExecutor):

  def __init__(self):
    super().__init__(
      extra_paths_segments_to_exclude=['/Library/'],
      extra_root_paths_to_exclude=['/Applications/','/System/']
    )

  def _generate_inputs_outputs(self, script: Script, output_file: str) -> int:
    """
    Calls the dtruss/dtrace command and outputs the file to the location specified. This method works with SIP
    enabled on the OS. It pairs opens and closes to find potential files for inputs and outputs. It then uses
    the modified timestamp of the file to determine whether it was read from or written to.

    We return the exit status of the script being run.

    :param script: The script command to run.
    :param output_file: The file to output the results of strace.
    """
    command_process = None
    dtruss_process_id = None
    try:

      click.echo('\nYou may be asked to enter your sudo password because the trace commands require sudo access.\n')
      # we verify that the user has sudo permissions since we were getting asked twice about sudo (the 2nd time
      # was when we were killing the dtruss process in the finally block.
      sudo_process = subprocess.run('sudo -v', shell=True)
      if sudo_process.returncode != 0:
        raise Exception('Invalid sudo credentials')

      with open(output_file, 'w') as trace_file:
        # we use os.setpgrp so that we are able to kill both of the processes that get created after running dtruss with
        # sudo. When you run a process with sudo it creates a process for the sudo command and then it creates another
        # process in the sudo context to run the actual command. To fix this, we set the process group id of the
        # child process to the process group id of this process so that we can kill all these processes by the process
        # group id.
        dtruss_process = subprocess.Popen(
          f'sudo dtruss -L -n {script.program_name}',
          shell=True,
          stderr=trace_file,
          stdout=subprocess.PIPE,
          text=True,
          preexec_fn=os.setpgrp
        )
        dtruss_process_id = dtruss_process.pid

        # we sleep for 5 seconds, to allow the dtruss we just started to startup. When there was no sleep, dtruss was
        # missing the commands. 3 secs worked but decided to give some buffer.
        command_process = subprocess.Popen(
          f'sleep 5 && {script.full_command}',
          shell=True,
          stderr=subprocess.PIPE,
          stdout=subprocess.PIPE,
          stdin=subprocess.PIPE,
          text=True
        )

        click.echo('------------------- Output from your Script START ---------------------')
        for line in command_process.stdout:
          click.echo(line)
        for line in command_process.stderr:
          click.echo(Fore.RED + line)
        click.echo('------------------- Output from your Script END ---------------------')

        command_process.wait()

        return command_process.returncode
    finally:
      click.echo('\nCleaning up dtrace/dtruss processes\n')
      if command_process:
        try:
          command_process.terminate()
        except subprocess.CalledProcessError:
          click.echo(Fore.RED + f'Unable to stop the process running your script. You can find them if you run "ps aux | grep "{script.program_name}"')
      if dtruss_process_id:
        pgid = os.getpgid(dtruss_process_id)
        # We need to use sudo here since the dtruss process was created with sudo. A non-sudo'd process
        # cannot kill a sudo'd process. We run the clark script without sudo and thus CANNOT call
        # dtruss_process.terminate()/.kill().
        try:
          subprocess.run(f'sudo kill {pgid}', shell=True, check=True)
          # when we shut down dtruss, the dtrace process hangs around this is the only way I could figure out to stop it
          # needed to sleep to give time to dtrace to output to the file. Without this, the file was not written if we
          # killed the process to early. A gave it a lot of time since this will depend on system resources.
          time.sleep(5)
          subprocess.run('ps aux | grep "dtrace.*-n" | grep -v "grep" | tr -s " " | cut -d " " -f 2 | xargs -I {} sudo kill -9 {}', shell=True, check=True)
        except subprocess.CalledProcessError:
          click.echo(Fore.RED + 'Unable to stop DTrace process. You can find them if you run "ps aux | grep "dtrace\|dtruss"')


  def _parse_trace_loglines(self, log_lines: List[str], execution: ExecutionExtraction) -> ExecutionExtraction:
    """
    Parses the log lines from dtruss/dtrace and returns a list of the inputs and outputs.

    Iterates through the list of commands a once and it keeps track of the files we opened and we closed by the
    file descriptors. Then once we have the list of files opened and closed, we split them into inputs and outputs
    by the modified timestamp. We ignore a variety of system files that are not inputs nor  outputs.

    :param log_lines: The lines from the strace log output.
    """
    # open => fd => filename
    file_dict = {
      OPEN: {},
    }

    inputs_and_outputs = []

    for line in log_lines:
      command_type = self._command_type(line)

      if command_type == OPEN:
        filepath, open_fd = self._extract_filepath_and_fd_from_open(line)
        if filepath is not None:
          file_dict[OPEN][str(open_fd)] = filepath

      elif command_type == CLOSE:
        close_fd = str(int(re.match(CLOSE_REGEX, line)[2], 16))
        if close_fd in file_dict[OPEN]:
          filepath = file_dict[OPEN][close_fd]
          if self._valid_file(filepath, script=execution.script):
            inputs_and_outputs.append(ScriptInputOutput(filepath=filepath))
          del file_dict[OPEN][close_fd]

    # now go through the files and split them based on when they were modified.
    for input_output in inputs_and_outputs:
      if self.execution_started > datetime.datetime.fromtimestamp(self.get_modified_time(input_output.filepath)):
        execution.add_input(input_output)
      else:
        execution.add_output(input_output)

    return execution

  def _command_type(self, line: str) -> str:
    """
    Determines the type of command in the log line. Returns null for any types that we do not care about.

    We only care about open and close lines. We filter any opens for directories and we filter missing syscalls.

    :param line: The strace log line.
    """

    # some syscalls are blocked by the process so ignore those.
    if 'error on enabled probe' in line:
      return None

    # do not want to include directories
    if re.match(OPEN_DIR_REGEX, line):
      return None

    if re.match(OPEN_REGEX, line):
      return OPEN
    elif re.match(CLOSE_REGEX, line):
      return CLOSE
    else:
      return None

  def _extract_filepath_and_fd_from_open(self, line: str) -> (str, str):
    """
    Gets the filepath from the line with an open command. We strip null terminators from the filepath since
    many of the strings have them.

    :param line: The line from an open command.

    # e.g open("/Users/kamil/workspace/CLI/scripts/testcases/1workflow_replace/input1A.csv\0", 0x1000000, 0x0)
    """
    match = re.match(OPEN_REGEX, line)

    if len(match.groups()) < 3:
      raise Exception(f'Unsupported open format for: {line}')

    filename = match[2].rstrip('\x00')
    fd = match[3]

    if filename in ['..', '.']:
      return None, None

    return filename, fd

  def _valid_file(self, filename: str, script: Script) -> bool:
    """
    Checks whether the file is one that we want to track and upload as an input or output. We ignore system files,
    compiled files and the script file we are executing.

    # we ignore reading of the file which was executed, system files and compiled files
    :param filename: The filename to check
    :param script: The script being run
    """
    return filename != script.filepath\
      and not script.filepath.endswith(filename) \
      and not filename.endswith(script.filepath)\
      and not self._file_to_exclude(filename)\
      and not self._compiled_file(filename)

  def get_modified_time(self, filename: str) -> float:
    """
    Gets the modified time for the filename. Separated out to make testing easier.

    :param filename: The file to get the modified date for
    """
    return pathlib.Path(filename).lstat().st_mtime
