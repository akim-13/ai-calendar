from fastapi import APIRouter, HTTPException, status
from backend.database import DBSession
from backend.schemas.events import EventSchema
from backend.services import events
from backend.services.events import EventNotFoundError

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/from_task/{task_id}", response_model=list[EventSchema])
def list_from_task(db: DBSession, task_id: int) -> list[EventSchema]:
    """List all events linked to a given task."""
    event_list = events.list_events_from_task(db, task_id)
    return [EventSchema.from_orm(e) for e in event_list]


@router.get("/from_user/{username}", response_model=list[EventSchema])
def list_from_user(db: DBSession, username: str) -> list[EventSchema]:
    """List all events belonging to a given user."""
    event_list = events.list_events_from_user(db, username)
    return [EventSchema.from_orm(e) for e in event_list]


@router.delete("/delete_from_task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_from_task(db: DBSession, task_id: int) -> None:
    """Delete all events associated with a given task."""
    try:
        events.delete_events_from_task(db, task_id)
    except EventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
