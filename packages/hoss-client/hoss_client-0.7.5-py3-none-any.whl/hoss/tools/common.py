from typing import List, Optional

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from rich.table import Table
from rich import box
from rich.align import Align


class TaskStatus(Enum):
    """Enum for setting the state of tasks"""
    WAITING = 0
    RUNNING = 1
    DONE = 2
    ERROR = -1


class ObjectStatus(Enum):
    """Enum for tracking the status of an object in the object store"""
    ERROR = -1
    UNKNOWN = 0
    DOES_NOT_EXIST = 1
    IN_PROGRESS = 2
    EXISTS = 3


@dataclass
class ObjectState:
    """Dataclass for tracking the state of a file to be uploaded or downloaded"""
    path: Path
    uri: str
    status: ObjectStatus
    msg: str
    size: Optional[int] = None
    is_dir: bool = False


def get_task_status(tasks: List[str], status: List[TaskStatus]) -> Align:
    """Take a list of task statuses and render a table

    Args:
        tasks: list of tasks
        status: list of TaskStatus values

    Returns:
        the rendered Table
    """
    table = Table(box=box.SIMPLE_HEAVY, show_footer=False)
    table_centered = Align.center(table)

    table.add_column("Status", no_wrap=True)
    table.add_column("Tasks", no_wrap=True)

    for t, s in zip(tasks, status):
        if s == TaskStatus.WAITING:
            table.add_row(":hourglass:", t)
        elif s == TaskStatus.RUNNING:
            table.add_row(":face_with_monocle:", t)
        elif s == TaskStatus.DONE:
            table.add_row(":white_check_mark:", t)
        elif s == TaskStatus.ERROR:
            table.add_row(":x:", t)
        else:
            table.add_row(":question:", t)

    return table_centered
