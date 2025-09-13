from datetime import datetime

from backend.misc.config import DATETIME_FORMAT


def convertToJson(obj: object) -> dict:
    """
    Converts all properties in an ORM object into JSON, which is returned as a dict.
    Note that datetime objects will be converted to a string format of a datetime.
    """

    # Converts to datetime format if input is a datetime object
    f = lambda x: x.strftime(DATETIME_FORMAT) if isinstance(x, datetime) else x  # noqa: E731

    return {key: f(value) for key, value in obj.__dict__.items() if not key.startswith("_")}
