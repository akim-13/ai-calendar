from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database.deps import yield_db
from backend.database.models import Standalone_Event
from backend.services import external_cal_sync
from backend.tools import calendar_to_events

router = APIRouter()


@router.post("/", status_code=200)
def add_calendar(data: dict, db: Session = Depends(yield_db)) -> dict[str, str]:
    """Add events from an external ICS calendar link into the database."""

    url = data.get("ics_url")
    if not url:
        return {"Error": "No ics URL provided"}

    db.query(Standalone_Event).filter(Standalone_Event.eventBy == url).delete()
    db.commit()

    new_events_dict = calendar_to_events.get_events_from_external_cal_link(url)
    if "Valid link" in new_events_dict:
        new_events = new_events_dict.get("Valid link")

        if new_events is None:
            raise HTTPException(status_code=400, detail="No events found at the provided URL.")

        for i in new_events:
            new_event = Standalone_Event(
                standaloneEventName=i[0],
                start=i[1],
                end=i[2],
                standaloneEventDescription=i[3],
                eventBy=i[4],
                username="joe",  # placeholder
            )
            db.add(new_event)
        db.commit()

        return {"status": "complete"}
    else:
        raise HTTPException(status_code=400, detail=new_events_dict.get("Error"))


@router.post("/sync_all")
def sync_all_calendars(db: Session = Depends(yield_db)) -> list[list]:
    """Resynchronise all duplicate external calendar sources and return their counts."""

    repeated_values = (
        db.query(
            Standalone_Event.eventBy,
            func.count(Standalone_Event.eventBy).label("num_repeated"),
        )
        .group_by(Standalone_Event.eventBy)
        .having(func.count(Standalone_Event.eventBy) > 1)
        .all()
    )

    repeated_values = [list(row) for row in repeated_values]

    for value in repeated_values:
        external_cal_sync.sync_db_with_external_cal(value[0], db)

    return repeated_values
