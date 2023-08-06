import boto3
import click

from clark.cache import CacheReaderWriter


class S3UploadResult(object):
  def __init__(self, success, error_message, files):
    """
    Value object that captures result of an S3 upload.

    :param success: Whether the upload succeeded.
    :type success: bool
    :param error_message: The error message if success = False. Else this will be None.
    :type error_message: str
    :param files: The list of files uploaded.
    :type files: list[src.executor.ScriptInputOutput]
    """
    self.success = success
    self.error_message = error_message
    self.files = files


class S3Uploader(object):
  def __init__(self, cache_reader: CacheReaderWriter):
    """
    Helper to upload files to S3.

    :param cache_reader: Reads the cache for information.
    """
    cache_details = cache_reader.read()

    self.bucket = cache_details.workflow_bucket
    self.access_key_id = cache_details.access_key_id
    self.secret_key = cache_details.secret_key

  def upload_files(self, workflow_uuid: str, files) -> S3UploadResult:
    """
    Uploads files to S3. Returns the files with the s3 information filled in.

    :param workflow_uuid: The workflow UUID that the files belong to.
    :param files: The files to upload.
    :type files: list[src.executor.ScriptInputOutput]
    :return: Returns none if there was an error.
    """
    client = self.client()
    for file in files:
      click.echo(f'Uploading {file.filepath} to S3.')
      try:
        s3path = f'workflows/{workflow_uuid}/files/{file.content_hash}'
        client.put_object(Bucket=self.bucket, Key=s3path, ServerSideEncryption='AES256', Body=open(file.filepath, "rb"))
        file.s3_path = f's3://{self.bucket}/{s3path}'
      except Exception as e:
        return S3UploadResult(success=False, error_message=str(e), files=files)

    return S3UploadResult(success=True, error_message=None, files=files)


  def client(self):
    return boto3.client(
      's3',
      aws_access_key_id=self.access_key_id,
      aws_secret_access_key=self.secret_key
    )