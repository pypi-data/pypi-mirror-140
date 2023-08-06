from typing import List, Optional, Dict
import asyncio
import concurrent.futures
from multiprocessing import Queue, Process
import queue
import traceback

import re
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
from boto3.s3.transfer import MB

import hoss
from hoss.dataset import DatasetRef, Dataset
from hoss.console import console
from hoss.tools.common import TaskStatus, ObjectState, ObjectStatus, get_task_status

# By design asyncio does not allow its event loop to be nested.
# This is a problem where the event loop is already running it's impossible to run tasks and wait for the result.
# Since Jupyter uses Tornado, the kernel will already be in an event loop. This call patches asyncio to let us
# use it in this module while running in something like Jupyter.
import nest_asyncio
nest_asyncio.apply()


def upload_directory(dataset_name: str, directory: str, namespace: str, endpoint: str,
                     skip: str, num_processes: int = 1, max_concurrency: int = 10, multipart_threshold: int = 32,
                     multipart_chunk_size: int = 32, metadata: Optional[Dict[str, str]] = None,
                     prefix: Optional[str] = None) -> None:
    """Function to upload a directory with a CLI interface for status

    This method will sort files by size, starting with the smallest first, and then upload them
    one at a time.

    Args:
        dataset_name: Name of the dataset to upload into
        directory: The directory containing the files to upload. The files will be uploaded to a directory with this
                   same name in the root of the dataset unless the 'prefix' value is explicitly set
        namespace: The namespace containing the dataset
        endpoint: The URL for the Hoss server that you are uploading to
        skip: A regex string of files that should be skipped
        num_processes: Number of processes to use when uploading files. If you have too many processes you'll run out
                       of bandwidth and uploads will timeout/fail. If you don't have enough, your upload could take
                       more time. In general, if you have lots of small files you benefit from more processes, and
                       if you have large files, you likely don't need that many because boto will use concurrent uploads
        max_concurrency: max concurrency used by boto when uploading an object and its parts
        multipart_threshold: threshold in megabytes to activate multipart uploads
        multipart_chunk_size: size in megabytes to use multipart uploads
        metadata: Optional dict of key-value pairs to write to all files as object metadata
        prefix: Optional prefix to where the files should be uploaded. If this is provided, the directory name will
                not be included in the object path.

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
    title.add_row("[b]Hoss Upload Tool[/b]")
    layout["title"].update(Panel(title, style="white on #957299"))

    # Set summary element
    summary_grid = Table(box=box.SIMPLE_HEAVY, show_footer=False)
    summary_grid_centered = Align.center(summary_grid)
    summary_grid.add_column(justify="right")
    summary_grid.add_column("Settings", justify="left")
    summary_grid.add_row("[b]Server:[/b]", endpoint)
    summary_grid.add_row("[b]Namespace:[/b]", namespace)
    summary_grid.add_row("[b]Dataset:[/b]", dataset_name)
    summary_grid.add_row("[b]Directory:[/b]", directory)
    layout["summary"].update(summary_grid_centered)

    tasks = ["Check for credentials",
             "Check server connectivity",
             "Check dataset exists",
             "Process directory",
             "Upload data",
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
    prepare_job_id = job_progress.add_task("[white]Preparing Upload", total=8)
    upload_job_id = job_progress.add_task("[white]Uploading Data", start=False)
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

        # set transfer settings
        ds.namespace.object_store.set_transfer_config(multipart_threshold * MB,
                                                      max_concurrency,
                                                      multipart_chunk_size * MB)

        job_progress.advance(prepare_job_id)

        # list files
        _log(f"Scanning directory for files.")
        files = filter(os.path.isfile, Path(directory).rglob('*'))
        job_progress.advance(prepare_job_id)

        # Sort files
        _log(f"Sorting files by size. The smallest files will upload first.")
        files_sorted = sorted(files, key=lambda x: os.stat(x).st_size)
        job_progress.advance(prepare_job_id)

        # Find files to skip if you need to and remove them from the list of files to upload
        if skip != "":
            _log(f"Processing skipped files.")
            skipped_cnt = 0
            skip_check = re.compile(r'{}'.format(skip))
            skip_files = [f for f in files_sorted if skip_check.match(f.name)]
            for f in skip_files:
                files_sorted.remove(f)
                skipped_cnt += 1

            _log(f"Skipped {skipped_cnt} files based on provided regex.")
        job_progress.advance(prepare_job_id)

        # Check which files do not exist in the object store and need to be uploaded
        # This works by providing the list of files to upload, and then concurrently making HEAD requests to the
        # object store. The result is a state object that is used for the rest of the process to track the file
        _log(f"Queuing {len(files_sorted)} files for upload.")
        _log(f"Checking if files exist in the target dataset...")
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        event_loop = asyncio.get_event_loop()
        object_check_results: List[ObjectState] = event_loop.run_until_complete(_check_if_ref_exists(executor,
                                                                                                     files_sorted,
                                                                                                     ds,
                                                                                                     directory,
                                                                                                     prefix))

        # Finish the "prepare" task in the UI and start the "upload" task
        job_progress.advance(prepare_job_id)
        layout["tasks"].update(get_task_status(tasks,
                                               [TaskStatus.DONE,
                                                TaskStatus.DONE,
                                                TaskStatus.DONE,
                                                TaskStatus.DONE,
                                                TaskStatus.WAITING]))
        job_progress.update(upload_job_id, total=len(files_sorted), description="[white]Uploading Data")
        job_progress.start_task(upload_job_id)

        # Populate Work Queue
        # Here we check the results of the HEAD operations that ran above.
        # If an object does not exist add it to the work queue. Otherwise handle the status for messaging to the user.
        work_queue = Queue()
        status_queue = Queue()
        uploaded_objs = list()
        exist_objs = list()
        errored_objs = list()
        num_to_upload = 0
        for r in object_check_results:
            if r.status == ObjectStatus.DOES_NOT_EXIST:
                if r.path.name == ".DS_Store":
                    # Manually skip .DS_Store files. Treat them as if they "exist"
                    exist_objs.append(r)

                # Add item to be uploaded
                work_queue.put(r)
                num_to_upload += 1
            elif r.status == ObjectStatus.EXISTS:
                exist_objs.append(r)
            elif r.status == ObjectStatus.ERROR:
                errored_objs.append(r)
            else:
                raise Exception(f"Unexpected Object State. Something went wrong. Try again: {r}")

        if len(exist_objs) <= 10:
            # If only a few got skipped print it out
            for r in exist_objs:
                _log(f"Skipping {r.path.relative_to(directory)}. File already exists.")
        else:
            # Lots got skipped, so just print a summary
            _log(f"Skipping {len(exist_objs)} files out of {len(files_sorted)} that already exist.")

        # Reset the boto3 client in the object store before pickling occurs.
        ds.namespace.object_store.reset_client()

        force_quit = False
        if num_to_upload > 0:
            _log(f"Uploading {num_to_upload} files.")
            # Create workers
            # We create the specified number of processes to work through upload items. This in theory could be selected
            # automatically or tune itself based on timeouts. If you have too many processes you'll run out of bandwidth
            # and uploads will timeout/fail. If you don't have enough, your upload could take more time. In general,
            # if you have lots of small files you benefit from more processes, and if you have large files, you likely
            # don't need that many because boto will use concurrent uploads.
            #
            # Since we pre-populate all work in the queue, workers will exit when the queue is empty.
            processes = [Process(target=_upload_worker,
                                 args=(work_queue, status_queue,
                                       ds, directory, prefix, metadata)) for _ in range(num_processes)]

            for p in processes:
                p.start()

            # Monitor Results and update the UI
            # Here we get a message from the status queue, waiting 1 second for something to appear. If no messages
            # arrive, we check to see if the work queue is empty. If the work queue is not empty, we continue looping.
            # If it is empty, we check to see if the status index is empty. If the status index is empty that means
            # no upload items are being tracked and all work has been done so we break out of the infinite loop.
            num_uploading = 1
            status_index = dict()
            while True:
                try:
                    object_state: ObjectState = status_queue.get(timeout=1)

                    if object_state.status == ObjectStatus.IN_PROGRESS:
                        # The received state indicates a file is just starting to upload.
                        # First, increment the log index of everything currently in the process of uploading since
                        # a new log line is about to be added
                        for key in status_index:
                            status_index[key]["log_idx"] += 1
                        # Add this new file to the status tracking
                        status_index[object_state.uri] = {"log_idx": 0, "upload_idx": num_uploading}
                        # Increment num_uploaded so the next file that is started will be marked properly
                        _log(f"[{num_uploading}/{num_to_upload}] Uploading {object_state.path.relative_to(directory)}..."
                             f" ({humanize.naturalsize(object_state.path.stat().st_size)}).")
                        num_uploading += 1
                    elif object_state.status == ObjectStatus.EXISTS:
                        # The received state indicates a file has completed an upload
                        # Load the status tracking information for the file to update the UI properly
                        status = status_index[object_state.uri]
                        # Add the object state to the collection of successful uploads
                        uploaded_objs.append(object_state)

                        _log(f"[{status['upload_idx']}/{num_to_upload}] Uploading "
                             f"{object_state.path.relative_to(directory)}...done! "
                             f"({humanize.naturalsize(object_state.path.stat().st_size)}).",
                             at_index=status['log_idx'])

                        # Since this file is now uploaded, remove it from status tracking and increment the progress bar
                        del status_index[object_state.uri]
                        job_progress.advance(upload_job_id)

                    elif object_state.status == ObjectStatus.ERROR:
                        # The received state indicates a file has errored. Save the state to the error collection
                        # Load the status tracking information for the file to update the UI properly
                        status = status_index[object_state.uri]
                        errored_objs.append(object_state)
                        _log(f"[{status['upload_idx']}/{num_to_upload}] Uploading "
                             f"{object_state.path.relative_to(directory)}...FAILED! "
                             f"({humanize.naturalsize(object_state.path.stat().st_size)}).",
                             at_index=status['log_idx'])

                        # Remove it from status tracking and increment the progress bar
                        del status_index[object_state.uri]
                        job_progress.advance(upload_job_id)
                    else:
                        raise Exception("Unexpected status received. System state unknown. Try upload again.")

                except queue.Empty:
                    if work_queue.empty():
                        if not status_index:
                            # If you get here, the message queue is empty (after waiting 1 second), the work queue is
                            # empty, and there are no uploads currently being tracked, so that means everything is done.
                            break
                except KeyboardInterrupt:
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

        # If force_quit is True, it means the user hit `ctrl+c` to try to stop the upload.
        if force_quit:
            _log(f"Upload terminated by user!")
            return

        # If errors occurred, re-print at the end so the user sees them
        if len(errored_objs) == 0:
            _log(f"Upload completed successfully!.")
        else:
            for o in errored_objs:
                _log(f"Failed to upload {o.path.as_posix()}: {o.msg}")
            _log(f"Upload completed with {len(errored_objs)} errors! Check for missing files.")

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


async def _check_if_ref_exists(executor, files: List[Path], dataset: Dataset,
                               directory: str, prefix: Optional[str]) -> List[ObjectState]:
    """This async function concurrently checks if the list of files exist in the object store

    Args:
        executor: executor to run asyncio tasks in
        files: list of files to check
        dataset: the dataset the files may exist in
        directory: the directory that the local files exist in (used to format paths in the object store)
        prefix: optional prefix where the files should exist. will be used instead of the directory if set

    Returns:
        a list of populated ObjectState instances
    """
    loop = asyncio.get_event_loop()
    tasks = []
    results = list()
    for f in files:
        ref = _get_ref(f, dataset, directory, prefix)
        tasks.append(loop.run_in_executor(executor, ref.exists))
        results.append(ObjectState(f, ref.uri, ObjectStatus.UNKNOWN, ""))

    completed = await asyncio.gather(*tasks, return_exceptions=True)

    for cnt, t in enumerate(completed):
        if isinstance(t, Exception):
            results[cnt].status = ObjectStatus.ERROR
            results[cnt].msg = str(t)
        else:
            if t is False:
                results[cnt].status = ObjectStatus.DOES_NOT_EXIST
            else:
                results[cnt].status = ObjectStatus.EXISTS

    return results


def _upload_worker(work_queue: Queue, status_queue: Queue, dataset: Dataset,
                   directory: str, prefix: Optional[str],
                   metadata: Optional[Dict[str, str]] = None) -> None:
    """Function that runs in its own process to consume the work queue and upload data

    Args:
        work_queue: Queue containing 'ObjectState' instances representing files to be uploaded
        status_queue: A queue to send 'ObjectState' instances for status in the UI/main process
        dataset: the dataset the files may exist in
        directory: the directory that the local files exist in (used to format paths in the object store)
        prefix: optional prefix where the files should exist. will be used instead of the directory if set
        metadata: An optional dict of key-value pairs what will be written as object metadata on every file

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
            # Send a message to the main process that the file upload has started
            obj_state.status = ObjectStatus.IN_PROGRESS
            status_queue.put(obj_state)

            # Attempt the upload, and if it succeeds set state to EXISTS so UI knows
            ref = _get_ref(obj_state.path, dataset, directory, prefix)
            ref.write_from(obj_state.path.as_posix(), metadata=metadata)
            obj_state.status = ObjectStatus.EXISTS

        except Exception:
            obj_state.status = ObjectStatus.ERROR
            obj_state.msg = traceback.format_exc()

        status_queue.put(obj_state)


def _get_ref(path: Path, ds: Dataset, directory: str, prefix: Optional[str] = None) -> DatasetRef:
    """Helper function to return a DatasetRef instances based on the configuration

    Args:
        path: path to the file to load into a ref
        ds: the dataset the files may exist in
        directory: the directory that the local files exist in (used to format paths in the object store)
        prefix: optional prefix where the files should exist. will be used instead of the directory if set

    Returns:
        a populated DatasetRef instance
    """
    if prefix:
        ref = ds / prefix / path.relative_to(directory).as_posix()
    else:
        session_folder = os.path.basename(directory)
        ref = ds / session_folder / path.relative_to(directory).as_posix()

    return ref
