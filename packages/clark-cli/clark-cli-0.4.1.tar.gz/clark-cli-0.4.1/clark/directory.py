import click

def list_n_print_current_dir(backend, details, cache_reader_writer):
  """
  Lists the current directory and prints the contents to screen

  :param backend: The Backend API to make the request to.
  :type backend.BackendApi
  :param details: The cache details to write to disk.
  :type details: cache.CacheDetails
  :param cache_reader_writer: The writer to use when persisting the cache details.
  :type cache_reader_writer: cache.CacheReaderWriter
  """
  list_response = backend.list_directory(current_dir_uuid=details.current_dir_uuid, list_dir_name='.')
  if len(list_response) > 0:
    # update the items just in case they changed
    details.current_dir_name = list_response['current_dir']['name']
    details.current_dir_items = list_response['items']
    cache_reader_writer.write(details)
    print_directory_contents(details.current_dir_name, details.current_dir_items)

def print_directory_contents(dir_item_name, folder_items):
  """
  Pretty prints the directory contents.

  :param dir_item_name: The name of the current directory.
  :type dir_item_name: str
  :param folder_items: A dict in the format:
  { "name1": {"uuid": string, "type": string }
  :type folder_items: dict
  """
  click.echo()
  click.echo('------------- {d} -------------'.format(d=dir_item_name))
  for name, details in folder_items.items():
    click.echo('{name} ({type})'.format(name=name, type=details['type']))
  click.echo()
