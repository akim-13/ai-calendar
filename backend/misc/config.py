import os
import sys

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "sqlite:///./database.db"
API_KEY = os.getenv("OPENAI_API_KEY")
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(level_colon)s %(name)-24s %(message)s (%(asctime)s)",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": sys.stdout,
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}
