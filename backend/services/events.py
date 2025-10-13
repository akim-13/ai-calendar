from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.database import Event, Task, User


class EventNotFoundError(Exception):
    """Raised when an event or related entity cannot be found."""

def list_events_from_task(db: Session, task_id: int) -> List[Event]:
    """Return all events linked to a given task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise EventNotFoundError(f"Task with ID {task_id} not found.")

    events = db.query(Event).filter(Event.task_id == task_id).all()
    return events

def list_events_from_user(db: Session, username: str) -> List[Event]:
    """Return all events belonging to a given user."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise EventNotFoundError(f"User '{username}' not found.")

    # Find all events for this user's tasks
    events = (
        db.query(Event)
        .join(Task, Event.task_id == Task.id)
        .filter(Task.username == username)
        .all()
    )
    return events

def delete_events_from_task(db: Session, task_id: int) -> None:
    """Delete all events associated with a given task ID."""
    events = db.query(Event).filter(Event.task_id == task_id).all()
    if not events:
        raise EventNotFoundError(f"No events found for task ID {task_id}.")

    for e in events:
        db.delete(e)
