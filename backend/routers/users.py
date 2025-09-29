from fastapi import APIRouter

from backend.database import DBSession
from backend.schemas import CreateUserRequest, UserSchema
from backend.services.users import create_user

router = APIRouter()


@router.post("/create", response_model=UserSchema)
def create(db: DBSession, request: CreateUserRequest) -> UserSchema:
    """Create a new user account."""
    user = create_user(db, request.username)
    return UserSchema.from_orm(user)
