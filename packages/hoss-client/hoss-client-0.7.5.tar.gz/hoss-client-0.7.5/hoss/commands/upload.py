import click
from hoss.tools.upload import upload_directory


@click.command()
@click.argument('dataset_name', metavar='DATASET_NAME', type=str, nargs=1)
@click.argument('directory', type=str, nargs=1)
@click.option('--namespace', '-n', type=str, default="default", show_default=True,
              help="Namespace that contains the dataset")
@click.option('--endpoint', '-e', type=str, default="http://localhost", show_default=True,
              help="Hoss server root endpoint")
@click.option('--prefix', '-p', type=str, default="",
              help="Optional prefix to where the files should be uploaded. If this is not provided, the files will be"
                   " uploaded to a 'directory' in the root of the dataset. The the 'directory' name will be the same"
                   " as the source directory name.")
@click.option('--skip', '-s', type=str, default="",
              help="Optional regular expression used to filter out files to skip (e.g. myprefix.*\\.txt)")
@click.option('--num_processes', '-j', type=int, default=1, show_default=True,
              help="Number of processes to use when uploading files. If you have too many processes you'll run out of "
                   "bandwidth and uploads will timeout/fail. If you don't have enough, your upload could take more "
                   "time. In general, if you have lots of small files you benefit from more processes, and if you "
                   "have large files, you likely don't need that many because boto will use concurrent uploads")
@click.option('--max_concurrency', '-c', type=int, default=10, show_default=True,
              help="Maximum number of concurrent s3 API transfer operations.")
@click.option('--multipart_threshold', type=int, default=32, show_default=True,
              help="Threshold in megabytes for which transfers will be split into multiple parts, defaults to 32MB")
@click.option('--multipart_chunk_size', type=int, default=32, show_default=True,
              help="Size in megabytes for each multipart chunk, if used. Defaults to 32MB")
@click.option('--metadata', '-m', type=str, multiple=True, default=list(),
              help="Object metadata key-value pair(s) applied to every object uploaded."
                   " You may specify multiple values by repeating the option (e.g. -m foo=bar -m fizz=buzz")
@click.pass_context
def upload(ctx, dataset_name: str, directory: str, namespace: str,
           endpoint: str, prefix: str, skip: str, num_processes: int, max_concurrency: int, multipart_threshold: int,
           multipart_chunk_size: int, metadata: str):
    """Upload files in a directory to an existing dataset"""
    # Convert metadata to dict if it is set, otherwise set to None
    if metadata:
        metadata_pairs = [item.split("=") for item in metadata]
        metadata_dict = dict((k.lower(), v.lower()) for k, v in metadata_pairs)
    else:
        metadata_dict = None

    if not prefix:
        prefix = None

    upload_directory(dataset_name, directory, namespace, endpoint, skip, num_processes,
                     max_concurrency, multipart_threshold, multipart_chunk_size, metadata_dict, prefix)
