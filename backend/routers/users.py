from fastapi import APIRouter

from backend.database import DBSession
from backend.schemas import CreateUserRequest, UserResponse
from backend.services.users import create_user

router = APIRouter()


@router.post("/create", response_model=UserResponse, operation_id="createUser")
def create_user_endpoint(db: DBSession, request: CreateUserRequest) -> UserResponse:
    """Create a new user account."""
    user = create_user(db, request.username)
    return UserResponse.model_validate(user)
