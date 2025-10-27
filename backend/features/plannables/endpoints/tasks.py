from fastapi import APIRouter, Depends
from features.plannables.schemas.tasks import TaskCreateForm, TaskUpdateForm
from infra.db import DBSession

# TODO: Createa an int-backed Enum class instead.
PRIORITY_LOW = 0
PRIORITY_MID = 1
PRIORITY_HIGH = 2

router = APIRouter()


@router.post("/")
def create_task(
    db: DBSession,
    form_data: TaskCreateForm = Depends(TaskCreateForm.as_form),
) -> None:
    """Create a new task, save it in the database, and schedule events for it."""
    db = db
    form_data = form_data
    raise NotImplementedError


@router.put("/{taskID}")
def update_task(
    db: DBSession,
    taskID: int,
    form_data: TaskUpdateForm = Depends(TaskUpdateForm.as_form),
) -> None:
    """Update an existing task and reschedule its events."""
    db = db
    taskID = taskID
    form_data = form_data
    raise NotImplementedError


@router.delete("/{taskID}")
def delete_task(db: DBSession, taskID: int) -> None:
    """Delete a task and its events."""
    db = db
    taskID = taskID
    raise NotImplementedError


@router.get("/user/{username}")
def list_user_tasks(db: DBSession, username: str) -> None:
    """Return all tasks for a user."""
    db = db
    username = username
    raise NotImplementedError


@router.get("/user/{username}/latest")
def get_latest_user_task(db: DBSession, username: str) -> None:
    """Return the most recent task for a user."""
    db = db
    username = username
    raise NotImplementedError
