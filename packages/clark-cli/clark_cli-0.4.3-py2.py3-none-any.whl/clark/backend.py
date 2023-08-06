import json
import base64

import requests
import click

from colorama import Fore

WORKFLOW = 'workflow'
DIRECTORY = 'directory'

class UploadResult(object):
  def __init__(self, success, error_message=''):
    """
    A value object to store the results of BackendApi.upload
    :param success: Whether the ndoes were successfully added.
    :type success: bool
    :param error_message: The error message if success = False
    :type error_message: str
    """
    self.success = success
    self.error_message = error_message

  def __repr__(self):
    if self.success:
      return Fore.GREEN + 'Upload Success: {s}'.format(s=self.success)
    else:
      return Fore.RED + 'Upload Success: {s}. Error: {e}'.format(s=self.success, e=self.error_message)


class BackendApi(object):
  def __init__(self, url, auth_token):
    """
    Interacts with the backend APIs

    :param url: The url of the backend API
    :type url: str
    :param auth_token: The token to use for authenticating requests.
    :type auth_token:str
    """
    self.url = url
    self.auth_token = auth_token

  def list_directory(self, current_dir_uuid, list_dir_name):
    """
    Calls the backend API to list the directories and workflows inside of list_dir_name which is inside of
    current_dir_uuid.

    :param current_dir_uuid: The UUID of the current directory (which is the parent of the directory that we are trying
    to list.
    :type: current_dir_uuid: str
    :param list_dir_name: The name of the directory to list which is inside of current_dir_uuid.
    :type list_dir_name: str
    :return: The dictionary response in the format of:
    { "current_dir": { "uuid": string },
      "items": { "name1": {"uuid": string, "type": string }, }
    }
    :rtype: dict
    """
    get_url = '{u}/v1/directory?current_dir_uuid={p}&child_dir_name={l}'.format(
      u=self.url,
      p=current_dir_uuid,
      l=list_dir_name
    )
    headers = {'Authorization': f'Bearer {self.auth_token}'}
    response = requests.get(url=get_url, headers=headers)

    if response.status_code == 200:
      response_json = response.json()
      items = dict([(el['name'], {'uuid': el['uuid'], 'type': el['type']}) for el in response_json['items']])
      return {
        'current_dir': response_json['current_dir'],
        'items': items
      }

    if response.status_code in [401, 403]:
      self.handle_401_403(server_error_string=response.json()['errors'][0])
    else:
      click.echo(Fore.RED + 'Unable to list directory because of error on backend. Status: {s}. Error: {e}'.format(
        s=response.status_code,
        e=response.json()['errors'][0]
      ))

    return {}

  def add_workflow(self, parent_dir_uuid, name):
    """
    Calls the backend API to add a new workflow with name 'name' inside of the directory 'parent_dir_uuid'.

    :param parent_dir_uuid: The UUID of the directory to add the workflow into.
    :type parent_dir_uuid: str
    :param name: The name of the workflow.
    :type name: str
    :return: The UUID of the new workflow.
    :rtype: str
    """
    post_url = '{u}/v1/workflow'.format(u=self.url)
    body = {
      "workflow": {
          "parent_uuid": parent_dir_uuid,
          "name": name,
      }
    }
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.auth_token}'}
    response = requests.post(url=post_url, data=json.dumps(body), headers=headers)
    if response.status_code == 201:
      return response.json()['uuid']

    if response.status_code in [401, 403]:
      self.handle_401_403(server_error_string=response.json()['errors'][0])
    else:
      click.echo(Fore.RED + 'Unable to add workflow because of error on backend. Status: {s}. Error: {e}'.format(
        s=response.status_code,
        e=response.json()['errors'][0]
      ))

    return None

  def add_directory(self, parent_dir_uuid, name):
    """
    Calls the backend API to add a new directory with name 'name' inside of the directory 'parent_dir_uuid'.

    :param parent_dir_uuid: The UUID of the directory to add the directory into.
    :type parent_dir_uuid: str
    :param name: The name of the directory.
    :type name: str
    :return: The UUID of the new directory.
    :rtype: str
    """
    post_url = '{u}/v1/directory'.format(u=self.url)
    body = {
      "directory": {
          "parent_uuid": parent_dir_uuid,
          "name": name,
      }
    }
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.auth_token}'}
    response = requests.post(url=post_url, data=json.dumps(body), headers=headers)
    if response.status_code == 201:
      return response.json()['uuid']

    if response.status_code in [401, 403]:
      self.handle_401_403(server_error_string=response.json()['errors'][0])
    else:
      click.echo(Fore.RED + 'Unable to add directory because of error on backend. Status: {s}. Error: {e}'.format(
        s=response.status_code,
        e=response.json()['errors'][0]
      ))

    return None

  def login(self, email, password):
    """
    Calls the backend API to retrieve a token that can be used for all subsequent requests.

    :param email: The email of the user
    :type email: str
    :param password: The user's password.
    :type password: str
    """
    get_url = '{u}/v1/user/login'.format(u=self.url)
    creds = base64.encodebytes(
      ('{e}:{p}'.format(e=email, p=password)).encode()
    ).decode().replace('\n', '')
    headers = {
      'Authorization': 'Basic {creds}'.format(creds=creds)
    }
    response = requests.get(url=get_url, headers=headers)
    if response.status_code == 200:
      return response.json()['auth']['token']

    return None

  def upload(self, workflow_uuid, inputs, script, outputs, message, files_to_replace):
    """
    Calls the backend API to upload a new script execution.

    :param workflow_uuid: The UUID of the workflow to add the execution to.
    :type workflow_uuid: str
    :param inputs: The input files to the script.
    :type inputs: list[src.executor.ScriptInputOutput]
    :param script: The script
    :type script: src.executor.ScriptInputOutput
    :param outputs: The output files to the script.
    :param message: The message to associate with the uploaded version.
    :type message: str
    :type inputs: list[src.executor.ScriptInputOutput]
    :param files_to_replace: A list of filenames to replace with script.
    :type files_to_replace: list[str]
    :rtype: UploadResult
    """
    post_url = '{u}/v1/workflow/upload'.format(u=self.url)
    inputs_to_send = [{"content_hash": i.content_hash, "filepath": i.s3_path, "user_filename": i.filename()} for i in inputs]
    outputs_to_send = [{"content_hash": o.content_hash, "filepath": o.s3_path, "user_filename": o.filename()} for o in outputs]
    body = {
      "workflow": {
        "uuid": workflow_uuid
      },
      "version": {
        "message": message,
      },
      "command": {
        "replace": len(files_to_replace) > 0
      },
      "inputs": inputs_to_send,
      "scripts": {
        "add": [
           {
             "content_hash": script.content_hash,
             "filepath": script.s3_path,
             "user_filename": script.filename()
           }
        ],
        "remove": [{'user_filename': f} for f in files_to_replace]
      },
      "outputs": outputs_to_send
    }
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.auth_token}'}
    response = requests.post(url=post_url, data=json.dumps(body), headers=headers)
    if response.status_code == 201:
      return UploadResult(success=True)

    response_body = response.json()

    if response.status_code in [401, 403]:
      self.handle_401_403(server_error_string=response_body['errors'][0])
      error_message = 'No access to workflow.'
    else:
      if 'errors' in response_body and len(response_body['errors']) > 0:
        error_message = '. '.join(response_body['errors'])
      elif 'outcome' in response_body:
        if response_body['outcome'] == 'ScriptFilenameExistsAlready':
          error_message = 'Script names must be unique within a workflow. Change the name of the script and re-run.'
        else:
          extra_info = response_body['outcome']
          error_message = f'Unknown error on server, prevented run. Code: {extra_info}'
      else:
          error_message = f'Unknown error on server. Status: {response.status_code}'

    return UploadResult(success=False, error_message=error_message)

  def get_config(self, token: str) -> dict:
    """
    Calls the backend API to retrieve the configuration. We provide a way to override the auth token since this call
    comes right after login.

    :param token: The auth token.
    """
    get_url = '{u}/v1/config'.format(u=self.url)
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url=get_url, headers=headers)
    body = response.json()
    if response.status_code == 200:
      return {
        'access_key_id': body['aws']['clark-user']['access_key_id'],
        'secret_key': body['aws']['clark-user']['secret_key'],
        'environment': body['environment']['ELIO_ENV'],
        'workflow_bucket': body['aws']['s3']['workflow']['bucket']
      }

    return None

  def handle_401_403(self, server_error_string):
    """
    Handles a HTTP 401 or 403 error

    :param server_error_string: The error string.
    :type server_error_string: str
    """
    click.echo(Fore.RED + "Unable to access server. Ensure you are logged in (e.g. call 'clark login') and that you are accessing the correct directory/workflow.")
    if server_error_string is not None:
      click.echo(Fore.RED + 'Server error message: {e}'.format(e=server_error_string))