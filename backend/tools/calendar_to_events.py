import requests
from ics import Calendar


def get_events_from_external_cal_link(link: str) -> None:
    raise NotImplementedError
    """Fetch events from an external ICS calendar link and return them as lists of attributes."""
    eventList = []

    try:
        file = requests.get(link)
    except Exception:
        return {"Error": "Invalid link"}

    if file.status_code != 200:
        return {"Error": "Invalid link"}

    file_type = file.headers.get("Content-Type", "")
    if "text/calendar" not in file_type and "application/octet-stream" not in file_type:
        return {"Error": "Invalid file type"}

    try:
        calendar = Calendar(file.text)
    except Exception:
        return {"Error": "Invalid ics format"}

    for event in calendar.events:
        start = event.begin.datetime
        end = event.end.datetime
        eventSingle = [event.name, start, end, event.description, link]
        eventList.append(eventSingle)

    return {"Valid link": eventList}
