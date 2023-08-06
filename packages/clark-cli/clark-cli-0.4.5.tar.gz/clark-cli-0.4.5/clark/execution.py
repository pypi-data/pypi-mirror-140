import os
import json
from hashlib import sha256


class ScriptInputOutput(object):
  def __init__(self, filepath: str):
    """
    A value object to hold information about a file.

    :param filepath: The FQ filename.
    """
    self.filepath = filepath
    self.content_hash : str = None
    self.s3_path : str = None

  def filename(self) -> str:
    """
    Returns the filename of the file path. For /a/b/c/d.txt returns d.txt.
    """
    return os.path.basename(self.filepath)

  def __repr__(self):
    return json.dumps(self.__dict__)

  def fill_content_hash(self):
    """
    Fills in the content_hash property. Have a separate function for this since it is a non-trivial operation and thus
    we want the client to be able to invoke it at the proper time since. It is non-trivial because it involves reading a
    (potentially large) file from disk and many errors can occur here.
    """
    # inspired by: https://www.quickprogrammingtips.com/python/how-to-calculate-sha256-hash-of-a-file-in-python.html
    sha256_hash = sha256()
    with open(self.filepath, "rb") as f:
      # Read and update hash string value in blocks of 4K
      for byte_block in iter(lambda: f.read(4096), b""):
        sha256_hash.update(byte_block)
    self.content_hash = sha256_hash.hexdigest()


class Script(ScriptInputOutput):
  def __init__(self, full_command: str):
    """
    A value object to hold information about the script being executed.

    :param full_command: The entire command to run which includes the the program_name, script_path and all arguments.
    """
    command_array = full_command.split(' ')
    if len(command_array) < 2:
      raise Exception('Command must have at least 2 words: executing program (e.g. python) and script file (e.g. script.py).')

    super().__init__(filepath=command_array[1])
    self.program_name = command_array[0]
    self.full_command = full_command


class ExecutionExtraction(object):
  def __init__(self, script: Script):
    """
    A value object to hold the details about an execution of a script

    :param script: The script that was executed
    """
    self.script = script
    self.inputs : [ScriptInputOutput] = []
    self.outputs : [ScriptInputOutput] = []
    self.exit_code = 0

  def __repr__(self):
    inputs_str = '\n'.join([json.dumps(i.__dict__) for i in self.inputs])
    outputs_str = '\n'.join([json.dumps(o.__dict__) for o in self.outputs])
    return f'Script:{json.dumps(self.script.__dict__)}\nInputs:{inputs_str}\nOutputs:{outputs_str}\n'

  def add_input(self, candidate_input: ScriptInputOutput):
    """
    Add the input to the list if it doesn't exist already. We check for existence since some programs read a file
    multiple times. We only care that the file was read once.

    :param candidate_input: The input to add to the list
    """
    if not any([1 for input in self.inputs if input.filepath == candidate_input.filepath]):
      self.inputs.append(candidate_input)

  def add_output(self, candidate_output: ScriptInputOutput):
    """
    Add the output to the list if it doesn't exist already. We check for existence since some programs write to a file
    multiple times. We only care that the file was written once.

    :param candidate_output: The output to add to the list
    """
    if not any([1 for output in self.outputs if output.filepath == candidate_output.filepath]):
      self.outputs.append(candidate_output)
