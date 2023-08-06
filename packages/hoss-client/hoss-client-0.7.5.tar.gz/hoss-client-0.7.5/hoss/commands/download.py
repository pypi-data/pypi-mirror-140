import click
from hoss.tools.download import download_prefix


@click.command()
@click.argument('dataset_name', metavar='DATASET', type=str, nargs=1)
@click.argument('namespace', type=str, nargs=1)
@click.argument('prefix', type=str, nargs=1)
@click.argument('destination', type=str, nargs=1)
@click.option('--endpoint', '-e', type=str, default="http://localhost", show_default=True,
              help="Hoss server root endpoint")
@click.option('--recursive', '-r', is_flag=True, show_default=True,
              help="If set, download all files with the prefix. Otherwise, only download files at the same level as the"
                   " prefix, assuming a `/` delimiter in the keys to represent 'directories'")
@click.option('--max_concurrency', '-c', type=int, default=10, show_default=True,
              help="max concurrency used when analyzing the prefix via requests to the object store")
@click.option('--num_processes', '-j', type=int, default=1, show_default=True,
              help="Number of processes to use when downloading files. If you have too many processes you'll run "
                   "out of bandwidth and downloads will timeout/fail. If you don't have enough, your download "
                   "could take more time. In general, if you have lots of small files you benefit from more processes,"
                   " and if you have large files, you likely don't need that many")
@click.pass_context
def download(ctx, dataset_name: str, namespace: str, prefix: str, destination: str,
             endpoint: str, recursive: bool, max_concurrency: int, num_processes: int):
    """Download files to a local directory from a prefix in a Dataset

    DATASET is the name of the dataset from which to download data

    NAMESPACE is the name of the namespace that contains the Dataset

    PREFIX is the prefix inside the dataset to download. Use "/" to indicate the root of the dataset.

    DESTINATION is the local directory to write files to
    """
    download_prefix(dataset_name, namespace, prefix, destination, endpoint, recursive,
                    num_processes, max_concurrency)
