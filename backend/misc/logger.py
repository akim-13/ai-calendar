import logging
import logging.config

from backend.misc.config import logging_config

# Logging level guidelines:
#
# DEBUG   – Detailed internal information, put them in when you write the code.
#           Example: "Querying DB with params {...}" or "Response payload {...}"
#
# INFO    – High-level application flow / normal operations.
#           Example: "User registered successfully" or "Server started on port 8000"
#
# WARNING – Something unexpected happened, but the app can still continue.
#           Example: "Cache miss, falling back to DB" or "Retrying connection..."
#
# ERROR   – A serious problem occurred; the operation failed.
#           Example: "Failed to save order to DB" or "Unhandled exception in request"
#
# CRITICAL– The application is in an unusable state, usually right before shutdown.
#           Example: "Database unavailable – terminating" or "Out of memory"


class ColonLevelFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Make a new attribute like "INFO:" or "WARNING:".
        level_with_colon: str = f"{record.levelname}:"
        # Pad that field so it's as wide as the longest level+colon.
        record.level_colon = level_with_colon.ljust(9)

        return super().format(record)


def configure_logging() -> None:
    """Configures logging parameters for Docker-friendly stdout logging."""
    logging.config.dictConfig(logging_config)
    for handler in logging.getLogger().handlers:
        if isinstance(handler.formatter, logging.Formatter):
            handler.setFormatter(
                ColonLevelFormatter(handler.formatter._fmt, handler.formatter.datefmt)
            )


def get_logger(name: str) -> logging.Logger:
    """Get logger named after the file where it's called."""
    name = format_logger_name(name)
    return logging.getLogger(f"[{name}]")


def format_logger_name(name: str) -> str:
    """Format logger name to be more readable."""
    # Remove "backend." prefix, and replace all "." with "/".
    return name.replace("backend.", "").replace(".", "/") + ".py"
