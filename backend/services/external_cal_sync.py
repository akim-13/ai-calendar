from sqlalchemy.orm import Session

from backend.database.models import Standalone_Event
from backend.tools import calendar_to_events


def sync_db_with_external_cal(cal_link: str, db: Session) -> None:
    """
    Replace all standalone events from a given calendar
    link with the latest events from that link.
    """

    db.query(Standalone_Event).filter(Standalone_Event.eventBy == cal_link).delete()
    db.commit()

    new_events = calendar_to_events.get_events_from_external_cal_link(cal_link)

    if "Valid link" in new_events:
        for event in new_events["Valid link"]:
            new_event = Standalone_Event(
                start=event[1],
                end=event[2],
                standaloneEventName=event[0],
                standaloneEventDescription=event[3],
                eventBy=event[4],
                username="joe",  # placeholder username
            )
            db.add(new_event)
        db.commit()
