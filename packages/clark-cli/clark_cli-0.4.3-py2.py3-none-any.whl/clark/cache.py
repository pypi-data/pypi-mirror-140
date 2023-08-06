import os
import json

import click
from colorama import Fore

class CacheDetails(object):
  def __init__(
      self,
      auth_token: str,
      current_dir_uuid: str,
      current_dir_name: str,
      open_workflow_uuid: str,
      current_dir_items: dict,
      access_key_id: str,
      secret_key: str,
      workflow_bucket: str,
      environment: str
  ):
    """
    A value object to store contents of the cache.

    :param auth_token: The token for the user, to be used when calling the backend API. Retrieved by calling the login
    command.
    :param current_dir_uuid: The current directory uuid. This is always populated unless in the root level. If a
    workflow is open, the current directory is the directory that is holding the workflow.
    :param current_dir_name: The name of the current directory that is referenced by current_dir_uuid.
    :param open_workflow_uuid: If the user has opened a workflow this will be populated, else it will be None. Used
    to determine if we are currently in a workflow.
    :param current_dir_items: A dictionary mapping directory entry names to dicts in the format:
    { "name": { "uuid": string, "type": string } }
    :param access_key_id: The access key id for uploads.
    :param secret_key: The secret key for uploads.
    :param workflow_bucket: The bucket to upload workflow files to.
    :pram environment: The environment we are operating in.
    """
    self.auth_token = auth_token
    self.current_dir_uuid = current_dir_uuid
    self.current_dir_name = current_dir_name
    self.open_workflow_uuid = open_workflow_uuid
    self.current_dir_items = current_dir_items
    self.access_key_id = access_key_id
    self.secret_key = secret_key
    self.workflow_bucket = workflow_bucket
    self.environment = environment

  @staticmethod
  def default_object():
    """
    Returns a empty object with "empty" and sensible defaults.
    :rtype: CacheDetails
    """
    return CacheDetails(
      auth_token=None,
      current_dir_uuid=None,
      current_dir_name=None,
      open_workflow_uuid=None,
      current_dir_items={},
      access_key_id=None,
      secret_key=None,
      workflow_bucket=None,
      environment=None
    )

  def in_workflow(self):
    """
    Determines if the user is currently in a workflow.

    :rtype: bool
    """
    return self.open_workflow_uuid is not None

class CacheReaderWriter(object):
  def __init__(self):
    """
    A class for reading and writing to/from the cache.

    file_path: The cache filepath on the local filesystem. Can use shell-like path expansions (e.g. '~')

    keys: The list of keys to read/write to the cache that will be populated in/to cache_template_object
    """
    self.file_path = os.path.expanduser('~/.clark/cache')
    self.keys = [
      'auth_token',
      'current_dir_uuid',
      'current_dir_name',
      'open_workflow_uuid',
      'current_dir_items',
      'access_key_id',
      'secret_key',
      'workflow_bucket',
      'environment'
    ]


  def read(self):
    """
    Reads the cache details from the filesystem and returns them.

    :rtype: CacheDetails
    """
    try:
      if not os.path.exists(self.file_path):
        self.write(CacheDetails.default_object())

      with open(self.file_path) as cache_file:
        cache_data = json.loads(cache_file.read())
        keys_to_populate = {k: v for k, v in cache_data.items() if k in self.keys}
        return CacheDetails(**keys_to_populate)
    except Exception as e:
      click.echo(Fore.RED + "Error reading cache. Please contact Elio. Error: {e}".format(e=e))
    return None

  def write(self, cache_details):
    """
    Writes the navigation cache to the filesystem.

    :param cache_details: The details to write to the cache
    :type cache_details: CacheDetails
    """
    try:
      # create intermediate directories if they do not exist
      os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
      with open(os.path.expanduser(self.file_path), "w+") as cache_file:
        cache_data = {k: v for (k,v) in cache_details.__dict__.items() if k in self.keys}
        cache_file.write(json.dumps(cache_data))
    except Exception as e:
      click.echo(Fore.RED + "Error reading cache. Please contact Elio. Error: {e}".format(e=e))
