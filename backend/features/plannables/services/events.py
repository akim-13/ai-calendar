from datetime import datetime

from sqlalchemy.orm import Session

from backend.core.entities import Event, Task, User
from backend.shared.config import DATETIME_FORMAT


def get_events(username: str, interval: tuple[datetime, datetime], db: Session) -> dict:
    """Return all events for the given user that fall within the provided time interval."""
    raise NotImplementedError

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        return {"events": []}

    user_events = user.events
    events = [event for event in user_events if interval[0] < event.start < interval[1]]
    events = events
    return None


def get_all_events(username: str, db: Session) -> dict:
    """Return all events for the given user in JSON format with start/end as strings."""
    raise NotImplementedError

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        return {"events": []}

    event_models: list[Event] = user.events
    events = [
        {
            "start": e.start.strftime(DATETIME_FORMAT),
            "end": e.end.strftime(DATETIME_FORMAT),
            "eventID": e.eventID,
            "title": e.task.title,
        }
        for e in event_models
    ]

    return {"events": events}


def edit_task_event(eventID: int, new_start: datetime, new_end: datetime, db: Session) -> dict:
    """Update the start and end time of a task event."""
    raise NotImplementedError

    event = db.query(Event).filter(Event.id == eventID).first()
    if event is None:
        return {"success": False, "message": "Event not found"}

    event.start = new_start
    event.end = new_end
    db.commit()

    return {"success": True}


def get_events_from_task(taskID: int, db: Session) -> dict:
    """Return all events belonging to a given task."""
    raise NotImplementedError

    tasks = db.query(Task).filter(Task.id == taskID).first()
    if tasks is None:
        return {"events": []}


def delete_events_from_task(taskID: int, db: Session) -> dict:
    """Delete all events associated with the given task ID."""
    raise NotImplementedError

    events = db.query(Event).filter(Event.id == taskID)
    events.delete()
    db.commit()

    return {"success": True}


def delete_task_event(eventID: int, db: Session) -> dict:
    """Delete a specific event by its ID."""
    raise NotImplementedError

    event = db.query(Event).filter(Event.id == eventID).first()
    if event is None:
        return {"success": False, "message": "Event not found"}

    db.delete(event)
    db.commit()

    return {"success": True}
