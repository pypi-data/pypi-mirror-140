from typing import List
import abc
import os
import pathlib
import datetime

import click

from clark.execution import ExecutionExtraction, Script


class ScriptExecutor(abc.ABC):

  def __init__(self):
    super().__init__()
    self.execution_started = None

  def extract(self, command: str) -> ExecutionExtraction:
    """
    Extracts the script and the inputs read by and outputs written by the command.

    :param command: The command line command to run.
    """
    self.execution_started = datetime.datetime.now()

    script = Script(full_command=command)
    script.fill_content_hash()
    execution = ExecutionExtraction(script=script)

    output_file = pathlib.Path('trace.log')
    if os.path.exists(str(output_file.absolute())):
      os.remove(str(output_file.absolute()))

    click.echo('Starting: Running script.')
    self._generate_inputs_outputs(script=script, output_file=str(output_file.absolute()))
    execution = self._parse_trace_log(output_file=str(output_file.absolute()), execution=execution)

    click.echo('Starting: Compute hashes for each input and output file.')
    for i in execution.inputs:
      i.fill_content_hash()
    for o in execution.outputs:
      o.fill_content_hash()

    return execution

  @abc.abstractmethod
  def _generate_inputs_outputs(self, script: Script, output_file: str):
    """
    Calls the strace command and outputs the file to the location specified.

    :param script: The script command to run.
    :param output_file: The file to output the results of strace.
    """
    pass

  def _parse_trace_log(self, output_file: str, execution: ExecutionExtraction) -> ExecutionExtraction:
    """
    Parses the result file from strace and returns a list of the inputs and outputs.

    :param output_file: The output file to parse.
    :param execution: The execution object that has the up to date results.
    """
    with open(output_file, 'r', errors='ignore') as log_file:
      log_lines = log_file.readlines()
      return self._parse_trace_loglines(log_lines=log_lines, execution=execution)

  @abc.abstractmethod
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
    pass