from sqlalchemy.orm import Session

from backend.database.models import Achievements, Standalone_Event, User
from backend.misc.defaults import default_achievements
from backend.misc.logger import get_logger
from backend.services import external_cal_sync

log = get_logger(__name__)


def startup(db: Session) -> None:
    """
    Run initialisation steps for the application:
    sync calendars, init achievements, seed user.
    """
    log.info("Running startup tasks...")
    update_all_external_cals(db)
    initialise_achievements(db)
    seed_joe_user(db)


def get_all_external_cal_sources(db: Session) -> list[str]:
    """Return all unique external calendar sources stored in the database."""
    sources = [
        source
        for (source,) in (
            db.query(Standalone_Event.eventBy)
            .filter(Standalone_Event.eventBy.isnot(None))
            .distinct()
            .all()
        )
    ]

    return sources


def update_all_external_cals(db: Session) -> None:
    """Resynchronise all external calendar sources with the database."""
    sources = get_all_external_cal_sources(db)
    for source in sources:
        external_cal_sync.sync_db_with_external_cal(source, db)


def initialise_achievements(db: Session) -> None:
    """Insert default achievements if none exist in the database."""
    if db.query(Achievements).count() == 0:
        for data in default_achievements:
            db.add(Achievements(**data))
        db.commit()


def seed_joe_user(db: Session) -> None:
    """Create a placeholder 'joe' user if it does not exist."""
    user = db.query(User).filter(User.username == "joe").first()
    if not user:
        db.add(
            User(
                username="joe",
                hashedPassword="x",
                streakDays=0,
                currentPoints=0,
                stressLevel=0,
            )
        )
        db.commit()
