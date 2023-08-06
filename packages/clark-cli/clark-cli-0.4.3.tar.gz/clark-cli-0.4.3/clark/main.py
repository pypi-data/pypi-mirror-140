from typing import List, Tuple
import sys
import os

import click
from colorama import init, Fore

from clark.cache import CacheReaderWriter
from clark.backend import BackendApi, DIRECTORY, WORKFLOW
from clark.directory import print_directory_contents, list_n_print_current_dir
from clark.xnix_executor import XnixScriptExecutor
from clark.mac_executor import MacScriptExecutor
from clark.execution import ScriptInputOutput
from clark.aws import S3Uploader

BACKEND_URL = os.environ.get('CLARK_NEST_BACKEND') or "https://nutcracker.clarknest.com"

cache_reader_writer = CacheReaderWriter()
backend: BackendApi = None # Populated in main
init(autoreset=True)

@click.group()
def main():
  """
  Tool to interact with research workflows. For issues email tech@elio.earth.

  For help with a specific command run clark [command] --help.
  """
  cache_details = cache_reader_writer.read()
  global backend

  # is None the first time we launch.
  if cache_details is None:
    backend = BackendApi(url=BACKEND_URL, auth_token=None)
  else:
    backend = BackendApi(url=BACKEND_URL, auth_token=cache_details.auth_token)


@main.command('login')
def login():
    """
    Login to the tool, must be done before all other commands.
    """
    email = click.prompt("Your Clark account email address")
    password = click.prompt("Password to your Clark account", hide_input=True)

    token = backend.login(email=email, password=password)
    if token is not None:
      config = backend.get_config(token=token)
      if config is not None:
        cache_details = cache_reader_writer.read()
        # on login erase all previous state
        cache_details = cache_details.default_object()
        cache_details.auth_token = token
        cache_details.access_key_id = config['access_key_id']
        cache_details.secret_key = config['secret_key']
        cache_details.workflow_bucket = config['workflow_bucket']
        cache_details.environment = config['environment']
        cache_reader_writer.write(cache_details)

        click.echo(Fore.GREEN + '\nLogged in successfully.\n')
      else:
        click.echo(Fore.RED + '\nError logging in. Login succeeded but configuration download failed. Try again please.')
    else:
      click.echo(Fore.RED + '\nError logging in. Check that email and password are correct.')


@main.command('ls')
def ls():
    """
    Prints out the contents of the current directory to the console.
    """

    details = cache_reader_writer.read()

    if details.in_workflow():
      click.echo(Fore.RED + "Unable to list the current directory because you are currently in a workflow. Run 'clark cd ..' to go back into a directory first.")
      return

    list_n_print_current_dir(backend=backend, details=details, cache_reader_writer=cache_reader_writer)


@main.command('cd')
@click.argument('dir_item_name', metavar='<name>')
def cd(dir_item_name):
    """
    Opens a directory or workflow from the current directory.

    For <name> you can use '..' to go up a level and '.' to list the current directory.

    Arguments:

    <name>: The name of the directory or workflow.
    """

    details = cache_reader_writer.read()

    # if in a workflow, check to make sure you are going up a level or else block the action.
    if details.in_workflow():
      if dir_item_name == '..':
        click.echo('\nClosing workflow.')
        details.open_workflow_uuid = None
        cache_reader_writer.write(details)
        list_n_print_current_dir(backend=backend, details=details, cache_reader_writer=cache_reader_writer)
      else:
        terminate(Fore.RED + "\nUnable to list the current directory because you are currently in a workflow. Run 'clark cd ..' to go back into a directory first.")
      return

    # if going into a directory/'..'/'.' or a directory we might not know about (e.g. was created elsewhere)
    if dir_item_name not in details.current_dir_items or details.current_dir_items[dir_item_name]['type'] == DIRECTORY:
      list_response = backend.list_directory(current_dir_uuid=details.current_dir_uuid, list_dir_name=dir_item_name)
      if len(list_response) == 0: # empty response
        click.echo(Fore.RED + "Unable to change to {i}".format(i=dir_item_name))
      else:
        details.current_dir_uuid = list_response['current_dir']['uuid']
        details.current_dir_name = list_response['current_dir']['name']
        details.current_dir_items = list_response['items']
        details.open_workflow_uuid = None
        cache_reader_writer.write(details)
        print_directory_contents(details.current_dir_name, details.current_dir_items)
    else: # going into a workflow
      workflow_uuid = details.current_dir_items[dir_item_name]['uuid']
      details.open_workflow_uuid = workflow_uuid
      cache_reader_writer.write(details)
      click.echo(Fore.GREEN + "\nOpened workflow '{w}'. Ready to execute methods.".format(w=dir_item_name))


@main.command('add')
@click.argument('item_type', metavar='<type>')
@click.argument('item_name', metavar='<name>')
def add_item(item_type, item_name):
  """
  Adds a new directory or workflow to the current directory.

  This action cannot be done while inside of a workflow. After the item is added, a print out of the current directory
  will be outputted which should contain the newly added item.

  Arguments:

    <type>: Either 'directory' or 'workflow'

    <name>: The name of the directory or workflow to add.
  """

  details = cache_reader_writer.read()

  if details.in_workflow():
    click.echo(Fore.RED + "Unable to add the {t} because you are currently in a workflow. Run 'clark cd ..' to go back into a directory first.".format(t=item_type))
    return

  if item_type == WORKFLOW or item_type == DIRECTORY:
    if item_type == WORKFLOW:
      uuid = backend.add_workflow(parent_dir_uuid=details.current_dir_uuid, name=item_name)
    else:
      uuid = backend.add_directory(parent_dir_uuid=details.current_dir_uuid, name=item_name)

    if uuid is not None:
      click.echo(Fore.GREEN + "Created {t} '{w}' successfully.".format(w=item_name, t=item_type))
      list_n_print_current_dir(backend=backend, details=details, cache_reader_writer=cache_reader_writer)
    else:
      click.echo(Fore.RED + "Error creating {t} '{w}.".format(w=item_name, t=item_type))
  else:
    click.echo(Fore.RED + 'Unknown type {t}'.format(t=item_type))


@main.command('upload')
@click.option('-r', '--replace', is_flag=True, help='Will replace the current file you are executing.')
@click.option('-rf', '--replace_files', metavar='<filename(s)>', help='A comma-separated list of filenames to replace with the script being run. (e.g --replace_files scriptA.py,scriptB.py)')
@click.option('-m', '--message', metavar='<message>', help='A message to attach to the version of the workflow that will be created.')
@click.argument('command', nargs=-1)
def upload(replace, replace_files, message, command):
  """
  Run the specified script in the command and update the workflow graph accordingly.

  Must be inside of a workflow for this command to work. This command can be quite heavy because in addition to
  running the script it has to upload the script, all inputs and all outputs to S3. Before uploading, it also has to
  re-read each file and generate a checksum of the file contents.

  Notes:

    - Does not support adding flags (e.g. script.py --flag) at this time.

    - On MacOS you will be asked for your sudo password due to the tracing program (dtrace) needing sudo privileges.

  """

  if replace and replace_files:
    terminate(Fore.RED + "Cannot use --replace (-r) and --replace_files (-rf) together."
                         " You more than likely just want to use --replace_files (-rf) and"
                         " list all the files you want to replace with this execution.")
    return

  command_str = ' '.join(command)

  # We expect the script filename to have at least 2 characters.
  if len(command_str) < 2:
    click.echo(Fore.RED + "Must enter a command to run. For help run 'clark upload --help'")
    return

  cache_details = cache_reader_writer.read()

  if not cache_details.in_workflow():
    return click.echo(Fore.RED + "You are not in a workflow. First 'cd' into a workflow before running a command.")

  if sys.platform == 'linux':
    executor = XnixScriptExecutor()
  elif sys.platform == 'darwin':
    executor = MacScriptExecutor()
  else:
    terminate('Your OS is not supported. Please contact tech@elio.earth.')
    return

  try:
    execution_result = executor.extract(command=command_str)
  except Exception as e:
    terminate(str(e))
    return

  click.echo(f'\nThe script run:\n{execution_result.script.filepath}')
  input_files_str = '\n'.join([i.filepath for i in execution_result.inputs])
  click.echo(f'\nThe inputs detected:\n{input_files_str}')
  output_files_str = '\n'.join([o.filepath for o in execution_result.outputs])
  click.echo(f'\nThe outputs detected:\n{output_files_str}')

  if execution_result.exit_code != 0:
    click.echo(Fore.YELLOW + f'\nYour program exited with non-zero exit code {execution_result.exit_code}.')

  prompt = '\nProceed to upload and modify workflow?\n' \
           'We provide the ability to modify the inputs in case a system file is detected ' \
           'that you would like to exclude. [Y]es/[N]o/[M]odify Inputs'
  proceed = click.prompt(prompt)

  response = proceed.lower()[0]
  if response not in ['y', 'm']:
    terminate(error_message='Nothing Uploaded')
    return

  if response == 'm':
    execution_result.inputs, excluded_inputs = choose_script_inputs(execution_result.inputs)
    new_input_files_str = '\n'.join([i.filepath for i in execution_result.inputs])
    click.echo(Fore.LIGHTGREEN_EX + f'\nThe NEW inputs:\n{new_input_files_str}')
    new_output_files_str = '\n'.join([i.filepath for i in excluded_inputs])
    click.echo(Fore.LIGHTRED_EX + f'\nThe EXCLUDED inputs:\n{new_output_files_str}')
    proceed = click.prompt('Is this correct? [Y]es/[N]o')
    if proceed.lower()[0] == 'n':
      terminate()
      return

  s3uploader = S3Uploader(cache_reader=cache_reader_writer)

  click.echo('\n')
  outputs_result = s3uploader.upload_files(workflow_uuid=cache_details.open_workflow_uuid, files=execution_result.outputs)
  if outputs_result.success is False:
    terminate(f'\nError uploading output datasets to AWS S3: {outputs_result.error_message}')
    return

  inputs_result = s3uploader.upload_files(workflow_uuid=cache_details.open_workflow_uuid, files=execution_result.inputs)
  if inputs_result.success is False:
    terminate(f'\nError uploading input datasets to AWS S3: {inputs_result.error_message}')
    return

  script_result = s3uploader.upload_files(workflow_uuid=cache_details.open_workflow_uuid, files=[execution_result.script])
  if script_result.success is False:
    terminate(f'\nError uploading script to AWS S3: {script_result.error_message}')
    return

  if replace_files:
    filenames_to_replace = replace_files.split(',')
  elif replace:
    filenames_to_replace = [execution_result.script.filename()]
  else:
    filenames_to_replace = []

  result = backend.upload(
    workflow_uuid=cache_details.open_workflow_uuid,
    script=script_result.files[0],
    inputs=inputs_result.files,
    outputs=outputs_result.files,
    message=message,
    files_to_replace=filenames_to_replace
  )
  click.echo(f'\n{result}')
  click.echo('\nComplete')


def choose_script_inputs(candidate_inputs: List[ScriptInputOutput]) -> Tuple[List[ScriptInputOutput], List[ScriptInputOutput]]:
  """
  Asks user to select which of the candidate script inputs should be considered valid.

  :param candidate_inputs: The list of script inputs
  :return: a tuple of files. First index has files selected, second index has files not selected.
  """
  key_to_inputs_map = {chr(idx + 97):input for idx, input in enumerate(candidate_inputs)}
  click.echo('\nBelow is the map of character to input.\n')
  for key, script_input in key_to_inputs_map.items():
    click.echo(f'{key}: {script_input.filepath}')
  letters = click.prompt("\nEnter letters that are inputs you want to keep as a single word (e.g. 'abfg')").replace(' ', '')
  return (
    [input for key, input in key_to_inputs_map.items() if key in letters],
    [input for key, input in key_to_inputs_map.items() if key not in letters]
  )

def terminate(error_message=None):
  if error_message:
    click.echo(Fore.RED + f'\n{error_message}')
  click.echo('\nExiting...\n')