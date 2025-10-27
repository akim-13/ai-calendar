from fastapi import APIRouter
from features.users.schemas import CreateUserRequest, UserResponse
from features.users.services import create_user
from infra.db import DBSession

router = APIRouter()


@router.post("/create", response_model=UserResponse, operation_id="createUser")
def create_user_endpoint(db: DBSession, request: CreateUserRequest) -> UserResponse:
    """Create a new user account."""
    user = create_user(db, request.username)
    return UserResponse.model_validate(user)
