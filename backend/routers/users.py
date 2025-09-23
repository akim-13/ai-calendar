from fastapi import APIRouter

from backend.database import DBSession

router = APIRouter()


@router.post("/create")
def create(db: DBSession, username: str) -> None:
    """Create a new user account."""
    db = db
    username = username
    raise NotImplementedError
