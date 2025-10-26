from sqlalchemy.orm import Session

from backend.shared.logger import get_logger

log = get_logger(__name__)


def startup(db: Session) -> None:
    """
    Run initialisation steps for the application:
    sync calendars, init achievements, seed user.
    """
    log.info("Running startup tasks...")
    log.warning("Not implemented yet.")
