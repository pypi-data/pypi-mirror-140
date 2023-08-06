from typing import List, Optional, Tuple
import asyncio
import concurrent.futures
from multiprocessing import Queue, Process
import queue
import traceback

import os
import time
import datetime
from pathlib import Path

import requests
from rich import box
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.style import Style
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.align import Align
from rich.layout import Layout

import humanize

import hoss
from hoss.utilities import etag_does_match
from hoss.dataset import Dataset
from hoss.console import console
from hoss.tools.common import TaskStatus, ObjectState, ObjectStatus, get_task_status

# By design asyncio does not allow its event loop to be nested.
# This is a problem where the event loop is already running it's impossible to run tasks and wait for the result.
# Since Jupyter uses Tornado, the kernel will already be in an event loop. This call patches asyncio to let us
# use it in this module while running in something like Jupyter.
import nest_asyncio
nest_asyncio.apply()


def download_prefix(dataset_name: str, namespace: str, prefix: str, destination: str, endpoint: str,
                    recursive: bool = False, num_processes: int = 1, max_concurrency: int = 10) -> None:
    """Function to download all objects in a prefix with a CLI interface for status

    This method will automatically skip files if they exist in the destination directory. If they exist, but
    are different, they will be overwritten with the object store's copy. This is done by hashing the file locally
    and comparing the result with the object's ETag.

    Args:
        dataset_name: Name of the dataset to download from
        namespace: The namespace containing the dataset
        prefix: Prefix inside the dataset to download. Use "/" to indicate the root of the dataset.
        destination: The directory to write files to.
        endpoint: The URL for the Hoss server that you are downloading from
        recursive: If True, download all files with the prefix. If false, only download files at the same level as the
                   prefix, assuming a `/` delimiter in the keys to represent "directories"
        num_processes: Number of processes to use when downloading files. If you have too many processes you'll run out
                       of bandwidth and downloads will timeout/fail. If you don't have enough, your download could take
                       more time. In general, if you have lots of small files you benefit from more processes, and
                       if you have large files, you likely don't need that many
        max_concurrency: max concurrency used when analyzing the prefix via requests to the object store

    Returns:
        None
    """
    log_msgs = list()

    console.clear()
    layout = Layout(name="root")

    def _log(msg: str, at_index: Optional[int] = None) -> None:
        """Helper method to update and build the log window contents

        Args:
            msg: log message to write
            at_index: if included, update the existing message at the provided index. Of omitted, prepend the message

        Returns:
            None
        """
        if at_index is not None:
            log_msgs[at_index] = f"{datetime.datetime.now().strftime('%H:%M:%S.%f %p')} - {msg}"
        else:
            log_msgs.insert(0, f"{datetime.datetime.now().strftime('%H:%M:%S.%f %p')} - {msg}")

        # Limit the number of messages that will be rendered to 100 lines (actual number depends on window height)
        if len(log_msgs) > 100:
            # pop off the oldest message
            _ = log_msgs.pop()

        log_panel = Panel(Text("\n".join(log_msgs)), title="[b]Status", border_style="#957299", padding=(1, 2),
                          expand=True)
        layout["status"].update(log_panel)

    # Initialize the layout
    layout.split(
        Layout(name="title", size=3),
        Layout(name="header", size=10),
        Layout(name="main", ratio=1),
    )
    layout["header"].split_row(
        Layout(name="summary"),
        Layout(name="tasks", ratio=1, minimum_size=60),
    )
    layout["main"].split_column(
        Layout(name="progress", size=10),
        Layout(name="status"),
    )

    # Set title element
    title = Table.grid(expand=True)
    title.add_column(justify="center", ratio=1)
    title.add_row("[b]Hoss Download Tool[/b]")
    layout["title"].update(Panel(title, style="white on #957299"))

    # Set summary element
    summary_grid = Table(box=box.SIMPLE_HEAVY, show_footer=False)
    summary_grid_centered = Align.center(summary_grid)
    summary_grid.add_column(justify="right")
    summary_grid.add_column("Settings", justify="left")
    summary_grid.add_row("[b]Server:[/b]", endpoint)
    summary_grid.add_row("[b]Namespace:[/b]", namespace)
    summary_grid.add_row("[b]Dataset:[/b]", dataset_name)
    summary_grid.add_row("[b]Prefix:[/b]", prefix)
    layout["summary"].update(summary_grid_centered)

    tasks = ["Check for credentials",
             "Check server connectivity",
             "Check dataset exists",
             "Analyze prefix",
             "Download data",
             ]

    layout["tasks"].update(get_task_status(tasks,
                                           [TaskStatus.WAITING,
                                            TaskStatus.WAITING,
                                            TaskStatus.WAITING,
                                            TaskStatus.WAITING,
                                            TaskStatus.WAITING]))

    # Initialize Progress section
    job_progress = Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(pulse_style=Style(color="#957299"), complete_style=Style(color="#957299")),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%", style=Style(color="#957299")),
        expand=True
    )
    prepare_job_id = job_progress.add_task("[white]Preparing Download", total=5)
    download_job_id = job_progress.add_task("[white]Downloading Data", start=False)
    layout['progress'].update(
        Align.center(Panel(job_progress, title="[b]Progress", border_style="#957299", padding=(1, 2), expand=False),
                     vertical="middle"))

    _log("Starting...")
    with Live(layout, console=console, refresh_per_second=30):
        # Check for PAT
        if not os.environ.get("HOSS_PAT"):
            # No credentials set
            _log("Personal Access Token not found!")
            layout["tasks"].update(get_task_status(tasks,
                                                   [TaskStatus.ERROR,
                                                    TaskStatus.WAITING,
                                                    TaskStatus.WAITING,
                                                    TaskStatus.WAITING,
                                                    TaskStatus.WAITING]))
            layout['progress'].update(
                Align.center(Panel("Failed to get personal access token from environment variable.\n\n"
                                   "Make sure you have set the `HOS_PAT` environment variable and try again."),
                             style="white on red", height=6))
            return
        else:
            _log("Personal Access Token found.")
            layout["tasks"].update(get_task_status(tasks,
                                                   [TaskStatus.DONE,
                                                    TaskStatus.RUNNING,
                                                    TaskStatus.WAITING,
                                                    TaskStatus.WAITING,
                                                    TaskStatus.WAITING]))
            job_progress.advance(prepare_job_id)
            time.sleep(1)

        try:
            _log("Connecting to server and exchanging credentials...")
            server = hoss.connect(endpoint)
            ns = server.get_namespace(namespace)
            _log("Server reachable and credentials ready.")
            layout["tasks"].update(get_task_status(tasks,
                                                   [TaskStatus.DONE,
                                                    TaskStatus.DONE,
                                                    TaskStatus.RUNNING,
                                                    TaskStatus.WAITING,
                                                    TaskStatus.WAITING]))
            job_progress.advance(prepare_job_id)
        except requests.exceptions.ConnectionError:
            layout["tasks"].update(get_task_status(tasks,
                                                   [TaskStatus.DONE,
                                                    TaskStatus.ERROR,
                                                    TaskStatus.WAITING,
                                                    TaskStatus.WAITING,
                                                    TaskStatus.WAITING]))
            _log(f"Server unreachable. Verify your network connection or endpoint setting.")
            layout['progress'].update(
                Align.center(Panel("Failed to reach server. \n\nCheck your endpoint and network connectivity.",
                                   style="white on red", height=6)))
            return
        except hoss.HossException as err:
            layout["tasks"].update(get_task_status(tasks,
                                                   [TaskStatus.DONE,
                                                    TaskStatus.ERROR,
                                                    TaskStatus.WAITING,
                                                    TaskStatus.WAITING,
                                                    TaskStatus.WAITING]))
            layout['progress'].update(Align.center(Panel(
                f"Failed to exchange credentials. \n\nVerify PAT with your Hoss server and try again. Error: \n\n {err}",
                style="white on red", height=10)))
            _log(f"Failed to exchange credentials.")
            return

        try:
            _log(f"Checking if dataset exists in the specified server and namespace.")
            ds = ns.get_dataset(dataset_name)
            # Hit the backend to load a boto client here in the main process/thread before handing this off for use.
            # If you don't do this here, it's likely you'll later have an issue when using the client.
            ds.exists()

            layout["tasks"].update(get_task_status(tasks,
                                                   [TaskStatus.DONE,
                                                    TaskStatus.DONE,
                                                    TaskStatus.DONE,
                                                    TaskStatus.RUNNING,
                                                    TaskStatus.WAITING]))
            _log(f"Dataset ready.")
            job_progress.advance(prepare_job_id)
        except hoss.NotFoundException:
            # Dataset does not exist
            layout['progress'].update(Align.center(
                Panel(f"Specified dataset does not exist. \n\nVerify input or create dataset and try again.",
                      style="white on red", height=6)))
            layout["tasks"].update(get_task_status(tasks,
                                                   [TaskStatus.DONE,
                                                    TaskStatus.DONE,
                                                    TaskStatus.DONE,
                                                    TaskStatus.ERROR,
                                                    TaskStatus.WAITING]))
            _log(f"Dataset not found. Please create it and try again.")
            return
        job_progress.advance(prepare_job_id)

        # Process the prefix and local directory
        # Check which files do not exist locally and collect them for download.v
        # If a file exists locally, make sure its content matches.
        _log(f"Processing prefix and local directory.")
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrency)
        event_loop = asyncio.get_event_loop()
        downloads, total_bytes = event_loop.run_until_complete(_populate_downloads(executor,
                                                                                   ds,
                                                                                   destination,
                                                                                   prefix,
                                                                                   recursive))
        job_progress.advance(prepare_job_id)

        _log(f"Total estimated size of download: {humanize.naturalsize(total_bytes)} ({len(downloads)} files)")
        if ds.namespace.object_store.object_store_type == "s3":
            # Warn about S3 egress.
            _log("NOTE: Downloading from S3 will incur egress costs at roughly $0.09 per GB downloaded. "
                 "Press `ctrl+c` to abort the download process.")
        time.sleep(5)

        # Finish the "prepare" task in the UI and start the "download" task
        layout["tasks"].update(get_task_status(tasks,
                                               [TaskStatus.DONE,
                                                TaskStatus.DONE,
                                                TaskStatus.DONE,
                                                TaskStatus.DONE,
                                                TaskStatus.WAITING]))
        job_progress.update(download_job_id, total=len(downloads), description="[white]Downloading Data")
        job_progress.start_task(download_job_id)

        # Populate Work Queue
        # Here we check the results of the HEAD operations that ran above.
        # If an object does not exist add it to the work queue. Otherwise handle the status for messaging to the user.
        work_queue = Queue()
        status_queue = Queue()
        downloaded_objs = list()
        exist_objs = list()
        errored_objs = list()
        num_to_download = 0
        for r in downloads:
            if r.status == ObjectStatus.DOES_NOT_EXIST:
                # Add item to be downloaded
                work_queue.put(r)
                num_to_download += 1
            elif r.status == ObjectStatus.EXISTS:
                exist_objs.append(r)
            elif r.status == ObjectStatus.ERROR:
                errored_objs.append(r)
            else:
                raise Exception(f"Unexpected Object State. Something went wrong. Try again: {r}")

        if len(exist_objs) <= 10:
            # If only a few got skipped print it out
            for r in exist_objs:
                _log(f"Skipping {r.path.relative_to(destination)}. File already exists.")
        else:
            # Lots got skipped, so just print a summary
            _log(f"Skipping {len(exist_objs)} files out of {len(downloads)} that already exist.")

        force_quit = False

        # Reset the boto3 client in the object store before pickling occurs.
        ds.namespace.object_store.reset_client()

        if num_to_download > 0:
            _log(f"Downloading {num_to_download} files.")
            # Create workers
            # We create the specified number of processes to work through downloads. This in theory could be selected
            # automatically or tune itself based on timeouts. If you have too many processes you'll run out of bandwidth
            # and downloads will timeout/fail. If you don't have enough, your download could take more time. In general,
            # if you have lots of small files you benefit from more processes, and if you have large files, you likely
            # don't need that many because boto will use concurrency.
            #
            # Since we pre-populate all work in the queue, workers will exit when the queue is empty.
            processes = [Process(target=_download_worker,
                                 args=(work_queue, status_queue,
                                       ds, destination, prefix)) for _ in range(num_processes)]
            for p in processes:
                p.start()

            # Monitor Results and update the UI
            # Here we get a message from the status queue, waiting 1 second for something to appear. If no messages
            # arrive, we check to see if the work queue is empty. If the work queue is not empty, we continue looping.
            # If it is empty, we check to see if the status index is empty. If the status index is empty that means
            # no download items are being tracked and all work has been done so we break out of the infinite loop.
            num_downloading = 1
            status_index = dict()
            while True:
                try:
                    object_state: ObjectState = status_queue.get(timeout=1)

                    if object_state.status == ObjectStatus.IN_PROGRESS:
                        # The received state indicates a file is just starting to download.
                        # First, increment the log index of everything currently in the process of downloading since
                        # a new log line is about to be added to the top
                        for key in status_index:
                            status_index[key]["log_idx"] += 1
                        # Add this new file to the status tracking since we'll have to update its log entry later
                        status_index[object_state.uri] = {"log_idx": 0, "download_idx": num_downloading}
                        # Increment num_downloading so the next file that is started will be marked properly
                        _log(f"[{num_downloading}/{num_to_download}] Downloading "
                             f"{object_state.path.relative_to(destination)}..."
                             f" ({humanize.naturalsize(object_state.size)}).")
                        num_downloading += 1
                    elif object_state.status == ObjectStatus.EXISTS:
                        # The received state indicates a file has completed an download
                        # Load the status tracking information for the file to update the UI properly
                        status = status_index[object_state.uri]
                        # Add the object state to the collection of successful downloads
                        downloaded_objs.append(object_state)

                        _log(f"[{status['download_idx']}/{num_to_download}] Downloading "
                             f"{object_state.path.relative_to(destination)}...done! "
                             f"({humanize.naturalsize(object_state.size)}).",
                             at_index=status['log_idx'])

                        # Since this file is now downloaded, remove it from status tracking and increment the progress bar
                        del status_index[object_state.uri]
                        job_progress.advance(download_job_id)

                    elif object_state.status == ObjectStatus.ERROR:
                        # The received state indicates a file has errored while being processed.
                        # Load the status tracking information for the file to update the UI properly
                        errored_objs.append(object_state)
                        if object_state.uri in status_index:
                            # The error happened while downloading
                            status = status_index[object_state.uri]
                            _log(f"[{status['download_idx']}/{num_to_download}] Downloading "
                                 f"{object_state.path.relative_to(destination)}...FAILED! "
                                 f"({humanize.naturalsize(object_state.size)}).",
                                 at_index=status['log_idx'])
                            # Remove it from status tracking
                            del status_index[object_state.uri]
                        else:
                            # You got an error before starting the download, so there is no message to update,
                            # log directly and increment the file count.
                            _log(f"[{num_downloading}/{num_to_download}] Downloading "
                                 f"{object_state.path.relative_to(destination)}...FAILED! "
                                 f"({humanize.naturalsize(object_state.size)}).")
                            num_downloading += 1

                        job_progress.advance(download_job_id)
                    else:
                        raise Exception("Unexpected status received. System state unknown. Try download"
                                        " again.")

                except queue.Empty:
                    if work_queue.empty():
                        if not status_index:
                            # If you get here, the message queue is empty (after waiting 1 second), the work queue is
                            # empty, and there are no downloads being tracked, so that means everything is done.
                            break
                except KeyboardInterrupt:
                    # The user is trying to quit, set the force_quit flag to message properly and exit
                    force_quit = True
                    break

            # Clean up any worker if they happen to still be running
            # (e.g. due to errors occurring so they don't gracefully exit)
            _log(f"Cleaning up processes.")
            for p in processes:
                if p.is_alive():
                    p.terminate()
                p.join()
                p.close()
            work_queue.close()
            status_queue.close()

        # If force_quit is True, it means the user hit `ctrl+c` to try to stop the download.
        if force_quit:
            _log(f"Download terminated by user!")
            return

        # If errors occurred, re-print at the end so the user sees them
        if len(errored_objs) == 0:
            _log(f"Download completed successfully!.")
        else:
            for o in errored_objs:
                _log(f"Failed to download {o.path.relative_to(destination)}: {o.msg}")
            _log(f"Download completed with {len(errored_objs)} errors! Check for missing files.")

        # Mark the task as done in the UI and wait a bit before exiting automatically
        layout["tasks"].update(get_task_status(tasks,
                                               [TaskStatus.DONE,
                                                TaskStatus.DONE,
                                                TaskStatus.DONE,
                                                TaskStatus.DONE,
                                                TaskStatus.DONE]))

        _log(f"Exiting in 15 seconds...")
        try:
            for cnt in range(15):
                _log(f"Exiting in {15-cnt} seconds...", at_index=0)
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        _log(f"Exiting.", at_index=0)

    console.clear()


async def _populate_downloads(executor, dataset: Dataset,
                              destination: str, prefix: str, recursive: bool) -> Tuple[List[ObjectState], int]:
    """function to concurrently check if the list of files exist in the object store and creates ObjectState instances

    Args:
        executor: executor to run asyncio tasks in
        dataset: the dataset the files may exist in
        destination: the destination directory where data is to be written
        prefix: Prefix inside the dataset to download. Use "/" to indicate the root of the dataset.
        recursive: If True, download all files with the prefix. If false, only download files at the same level as the
                   prefix, assuming a `/` delimiter in the keys to represent "directories"

    Returns:
        a list of populated ObjectState instances, total size of all files in bytes
    """
    loop = asyncio.get_event_loop()

    # Get all the refs in the object store at the specified prefix
    root_ref = dataset / prefix
    if recursive:
        refs = root_ref.rglob("*")
    else:
        refs = root_ref.glob("*")

    # For every ref, check if it exists locally and then create an ObjectStatus instance
    results: List[ObjectState] = list()
    to_verify = list()
    total_bytes = 0
    for r in refs:
        if prefix == "/":
            key_relative_to_prefix = r.key[len(f"{dataset.dataset_name}/"):]
        else:
            key_relative_to_prefix = r.key[len(f"{dataset.dataset_name}/{prefix}"):]

        p = Path(destination, key_relative_to_prefix)
        try:
            if r.is_file():
                if p.exists():
                    # If the file exists locally, add it to a list of files that should be checked for content changes
                    to_verify.append((p, r))
                else:
                    results.append(ObjectState(p, r.uri, ObjectStatus.DOES_NOT_EXIST, "", r.size_bytes))
                    total_bytes += r.size_bytes
            else:
                # Set the `is_dir` attribute to True. This will make the download worker simply create the directory
                # locally instead of try to download anything. This is because object store don't actually represent
                # folders, but imply infer them via convention.
                results.append(ObjectState(p, r.uri, ObjectStatus.DOES_NOT_EXIST, "", 0, is_dir=True))
        except Exception as err:
            results.append(ObjectState(p, r.uri, ObjectStatus.ERROR, str(err)))

    # For refs that exist locally, check if their content has changed. If the content is different
    # modify the status to DOES_NOT_EXIST so they are re-downloaded.
    tasks = []
    for data in to_verify:
        path, ref = data
        tasks.append(loop.run_in_executor(executor, etag_does_match, ref, path.as_posix()))

    completed = await asyncio.gather(*tasks, return_exceptions=True)

    for t, d in zip(completed, to_verify):
        path, ref = d
        if isinstance(t, Exception):
            results.append(ObjectState(path, ref.uri, ObjectStatus.ERROR, str(t)))
        else:
            if t is False:
                results.append(ObjectState(path, ref.uri, ObjectStatus.DOES_NOT_EXIST, "", ref.size_bytes))
                total_bytes += ref.size_bytes
            else:
                results.append(ObjectState(path, ref.uri, ObjectStatus.EXISTS, "", ref.size_bytes))

    return results, total_bytes


def _download_worker(work_queue: Queue, status_queue: Queue, dataset: Dataset,
                     destination: str, prefix: str) -> None:
    """Function that runs in its own process to consume the work queue and download data

    Args:
        work_queue: Queue containing 'ObjectState' instances representing files to be downloaded
        status_queue: A queue to send 'ObjectState' instances for status in the UI/main process
        dataset: the dataset the files may exist in
        destination: the destination directory where data is to be written
        prefix: Prefix inside the dataset to download. Use "/" to indicate the root of the dataset.

    Returns:
        None
    """
    # Reset the boto3 client in the object store that was passed in. This is important to do before the client is
    # used across processes as this is not a safe operation.
    dataset.namespace.object_store.reset_client()

    while True:
        try:
            obj_state: ObjectState = work_queue.get(timeout=1)
        except queue.Empty:
            # When the work queue is empty the process should exit
            return

        try:
            # Send a message to the main process that the file download has started
            obj_state.status = ObjectStatus.IN_PROGRESS
            status_queue.put(obj_state)

            # Create a directory for the data locally if needed
            p = Path(obj_state.path)
            if not p.parent.exists():
                # Create parent directory if needed, keeping exist_ok=True in case another process creates the
                # directory before this process does
                p.parent.mkdir(parents=True, exist_ok=True)

            # Attempt the download, and if it succeeds set state to EXISTS so UI knows
            if not obj_state.is_dir:
                ref = dataset / prefix / obj_state.path.relative_to(destination).as_posix()
                ref.read_to(obj_state.path.as_posix())
            else:
                # If it's a directory and not actually a file, create the directory
                p.mkdir(parents=True, exist_ok=True)
            obj_state.status = ObjectStatus.EXISTS

        except Exception:
            obj_state.status = ObjectStatus.ERROR
            obj_state.msg = traceback.format_exc()

        status_queue.put(obj_state)
