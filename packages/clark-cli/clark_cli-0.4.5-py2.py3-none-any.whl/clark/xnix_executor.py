import re
import subprocess
from typing import List

import click
from colorama import Fore

from clark.execution import ExecutionExtraction, ScriptInputOutput, Script
from clark.executor import ScriptExecutor


START_NUM_REGEX = re.compile(r"(^\d+\s*)", re.IGNORECASE)
PID_INFO_REGEX = re.compile(r"(^\[pid \d+\]\s*)", re.IGNORECASE)
CLOSE_FD_REGEX = re.compile(r"close\((\d+)", re.IGNORECASE)

OPENAT = 'openat('
READ = 'read('
WRITE = 'write('
CLOSE = 'close('
UNFINISHED = 'unfinished'
OPENAT_RESUMED = 'openat resumed'
CLOSE_RESUMED = 'close resumed'
READ_RESUMED = 'read resumed'
WRITE_RESUMED = 'write resumed'


class XnixScriptExecutor(ScriptExecutor):

  def __init__(self):
    super().__init__(
      extra_paths_segments_to_exclude=['/home/ubuntu/'],
      extra_root_paths_to_exclude=[]
    )

  def _generate_inputs_outputs(self, script: Script, output_file: str):
    """
    Calls the strace command and outputs the file to the location specified. Returns the return status of the code.

    :param script: The script command to run.
    :param output_file: The file to output the results of strace.
    """
    strace_command = f"strace -f -e trace=close,openat,write,read -o {output_file} {script.full_command}"
    completed_process = subprocess.run(strace_command, shell=True, capture_output=True, text=True)
    click.echo('------------------- Output from your Script START ---------------------')
    click.echo(completed_process.stdout)
    click.echo(Fore.RED + completed_process.stderr)
    click.echo('------------------- Output from your Script END ---------------------')

    return completed_process.returncode

  def _parse_trace_loglines(self, log_lines: List[str], execution: ExecutionExtraction) -> ExecutionExtraction:
    """
    Parses the log lines from strace and returns a list of the inputs and outputs.

    Iterates through the list of commands a once and it keeps track of the state (open, read, write) of each
    file descriptor. Once we encounter a close command we look at whether the file descriptor (fd) was written
    or read and we add the file to the inputs or outputs respectively. Before adding, we ignore some types of files.

    There is an extra complication where opens, reads, writes can get interrupted with words like "unfinished" and
    "resumed" and we need special handling for these cases.

    :param log_lines: The lines from the strace log output.
    """
    # open/read/written => fd => filename
    file_dict = {
      OPENAT: {},
      READ: {},
      WRITE: {}
    }

    for line in log_lines:
      line = self._strip_pid_information(line)
      command_type = self._command_type(line)

      if command_type == OPENAT:
        filename = self._extract_filename_from_openat(line)
        if 'unfinished' in line:
          file_dict[OPENAT][UNFINISHED] = filename
        else:
          # get the file descriptor; at the end of the line but don't copy newline (-1)
          open_fd = int(line[(line.rfind('= ') + 2):-1])
          file_dict[OPENAT][str(open_fd)] = filename

      elif command_type == WRITE:
        # get the file descriptor between ( )
        write_fd = int(line[line.find("(") + 1: line.find(",")])
        # need this protection because we saw some system files which were being written to
        # without being opened.
        if str(write_fd) in file_dict[OPENAT]:
          file_dict[WRITE][str(write_fd)] = file_dict[OPENAT][str(write_fd)]

      elif command_type == READ:
        # get the file descriptor between ( )
        read_fd = int(line[line.find("(") + 1: line.find(",")])
        if str(read_fd) in file_dict[OPENAT]:
          file_dict[READ][str(read_fd)] = file_dict[OPENAT][str(read_fd)]

      elif command_type == CLOSE:
        close_fd = int(re.findall(CLOSE_FD_REGEX, line)[0])
        if str(close_fd) in file_dict[WRITE]:
          filename = file_dict[WRITE][str(close_fd)]
          if self._valid_file(filename, executed_filename=execution.script.filename()):
            if filename[0] == '/':
              # absolute path
              execution.add_output(ScriptInputOutput(filepath=filename))
            else:
              if filename[:2] == './':
                filename = filename[2:]
              execution.add_output(ScriptInputOutput(filepath=self._absolute_path(filename)))
          del file_dict[OPENAT][str(close_fd)]
          del file_dict[WRITE][str(close_fd)]
        elif str(close_fd) in file_dict[READ]:
          filename = file_dict[READ][str(close_fd)]
          if self._valid_file(filename, executed_filename=execution.script.filename()):
            if filename[0] == '/':
              # absolute path
              execution.add_input(ScriptInputOutput(filepath=filename))
            else:
              if filename[:2] == './':
                filename = filename[2:]
              execution.add_input(ScriptInputOutput(filepath=self._absolute_path(filename)))
          del file_dict[OPENAT][str(close_fd)]
          del file_dict[READ][str(close_fd)]

      elif command_type == OPENAT_RESUMED:
        open_fd = int(line[(line.rfind('= ') + 2):-1])
        if UNFINISHED in file_dict[OPENAT]:
          file_dict[OPENAT][str(open_fd)] = file_dict[OPENAT][UNFINISHED]
          del file_dict[OPENAT][UNFINISHED]

    return execution


  def _strip_pid_information(self, line: str) -> str:
    """
    Strips any PID information which happens when a command was executed inside of another process. Also strips
    numbers from the beginning of each line. This happens when you add the -o option to the strace command.

    e.g. [pid 11739] openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
    and 11739 openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
    """
    line = re.sub(PID_INFO_REGEX, '', line)
    return re.sub(START_NUM_REGEX, '', line)


  def _command_type(self, line: str) -> str:
    """
    Determines the type of command in the log line. Returns null for any types that we do not care about.

    We only care about openat, read, write and close lines. We filter any opens for directories and we filter
    missing files too.

    :param line: The strace log line.
    """
    # This is a directory and hence we should skip it
    if 'O_DIRECTORY' in line:
      return None

    # if we couldn't read the file ignore it
    if 'No such file or directory' in line or 'ENOENT' in line:
      return None

    if line.startswith(OPENAT):
      return OPENAT
    elif line.startswith(WRITE):
      return WRITE
    elif line.startswith(CLOSE):
      return CLOSE
    elif line.startswith(READ):
      return READ
    elif WRITE_RESUMED in line:
      return WRITE_RESUMED
    elif READ_RESUMED in line:
      return READ_RESUMED
    elif OPENAT_RESUMED in line:
      return OPENAT_RESUMED
    elif CLOSE_RESUMED in line:
      return CLOSE_RESUMED
    else:
      return None


  def _extract_filename_from_openat(self, line: str) -> str:
    """
    Gets the filename from the line with an openat command.

    :param line: The line from an openat command.

    # e.g ['AT_FDCWD', '"./ls.txt"', 'O_RDWR|O_CREAT|O_TRUNC|O_CLOEXEC', '0666', '=4\n']
    """
    # This array holds all the arguments that you seen in an openat command
    ret_arr = [''] * 5
    args = 0
    inQuotation = 0
    for i in range(7, len(line)):
      if line[i] == '\"':
        inQuotation = 1 - inQuotation
      if line[i] == ',' and not inQuotation:
        args += 1
        continue
      if line[i] == ' ' and not inQuotation:
        continue
      if line[i] == ')' and not inQuotation:
        args += 1
        continue
      ret_arr[args] += line[i]

    # index 1 contains the file name and then remove the first and last character, which are "" (quotes)
    filename = ret_arr[1][1:-1]

    return filename

  def _valid_file(self, filename: str, executed_filename: str) -> bool:
    """
    Checks whether the file is one that we want to track and upload as an input or output. We ignore system files,
    compiled files and the script file we are executing.

    # we ignore reading of the file which was executed, system files and compiled files
    :param filename: The filename to check
    :param executed_filename: The script filename
    """

    return filename != executed_filename\
           and not filename.endswith(executed_filename) \
           and not executed_filename.endswith(filename) \
           and not self._file_to_exclude(filename)\
           and not self._compiled_file(filename)
