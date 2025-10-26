from fastapi import APIRouter

from backend.infra.db import DBSession

router = APIRouter()


@router.get("/list_from_task/{task_id}")
def list_events_from_task(db: DBSession, task_id: int) -> None:
    """Return all events linked to a given task."""
    db = db
    task_id = task_id
    raise NotImplementedError


@router.get("/list_from_user/{username}")
def list_events_from_user(db: DBSession, username: str) -> None:
    """Return all events belonging to a given user."""
    db = db
    username = username
    raise NotImplementedError


@router.delete("/delete_all_from_task/{task_id}")
def delete_events_from_task(db: DBSession, task_id: int) -> None:
    """Delete all events associated with a task."""
    db = db
    task_id = task_id
    raise NotImplementedError
