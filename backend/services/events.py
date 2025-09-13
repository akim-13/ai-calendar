from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.database.models import Event, Standalone_Event, Task, User
from backend.misc.config import DATETIME_FORMAT
from backend.tools.jsonify import convertToJson


def get_events(username: str, interval: tuple[datetime, datetime], db: Session) -> dict:
    """Return all events for the given user that fall within the provided time interval."""

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        return {"events": []}

    user_events = user.events
    events = [event for event in user_events if interval[0] < event.start < interval[1]]

    return {"events": [convertToJson(event) for event in events]}


def get_all_events(username: str, db: Session) -> dict:
    """Return all events for the given user in JSON format with start/end as strings."""

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

    event = db.query(Event).filter(Event.eventID == eventID).first()
    if event is None:
        return {"success": False, "message": "Event not found"}

    event.start = new_start
    event.end = new_end
    db.commit()

    return {"success": True}


def get_standalone_events(username: str, interval: tuple[datetime, datetime], db: Session) -> dict:
    """Return all standalone events for the given user within the specified interval."""

    events = (
        db.query(Standalone_Event)
        .filter(
            Standalone_Event.username == username,
            Standalone_Event.start > interval[0],
            Standalone_Event.start < interval[1],
        )
        .all()
    )

    return {"standalone_events": [convertToJson(event) for event in events]}


def get_latest_standalone_event(username: str, db: Session) -> dict:
    """
    Return the most recently created standalone event
    for the given user, or None if none exist.
    """

    latest_standalone_event = (
        db.query(Standalone_Event)
        .filter(Standalone_Event.username == username)  # fixed bug here
        .order_by(desc(Standalone_Event.standaloneEventID))
        .first()
    )

    if latest_standalone_event:
        return {"latest_standalone_event": convertToJson(latest_standalone_event)}
    else:
        return {"latest_standalone_event": None}


def edit_standalone_event(
    standaloneEventID: int,
    standaloneEventName: str,
    standaloneEventDescription: str,
    start: datetime,
    end: datetime,
    db: Session,
) -> dict:
    """Update the details of a standalone event if it exists."""

    standalone_event = (
        db.query(Standalone_Event)
        .filter(Standalone_Event.standaloneEventID == standaloneEventID)
        .first()
    )

    if standalone_event is None:
        return {"success": False, "message": "Event not found"}

    standalone_event.standaloneEventName = standaloneEventName
    standalone_event.standaloneEventDescription = standaloneEventDescription
    standalone_event.start = start
    standalone_event.end = end
    db.commit()

    return {"success": True}


def get_events_from_task(taskID: int, db: Session) -> dict:
    """Return all events belonging to a given task."""

    tasks = db.query(Task).filter(Task.taskID == taskID).first()
    if tasks is None:
        return {"events": []}

    return {"events": [convertToJson(event) for event in tasks.events]}


def delete_events_from_task(taskID: int, db: Session) -> dict:
    """Delete all events associated with the given task ID."""

    events = db.query(Event).filter(Event.taskID == taskID)
    events.delete()
    db.commit()

    return {"success": True}


def delete_task_event(eventID: int, db: Session) -> dict:
    """Delete a specific event by its ID."""

    event = db.query(Event).filter(Event.eventID == eventID).first()
    if event is None:
        return {"success": False, "message": "Event not found"}

    db.delete(event)
    db.commit()

    return {"success": True}
