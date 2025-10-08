from fastapi import APIRouter

from backend.database import DBSession
from backend.schemas import *
from backend.services.users import *

router = APIRouter()


@router.post("/create", response_model=UserSchema)
def create(db: DBSession, request: CreateUserRequest) -> UserSchema | None:
    """Create and return new user account. If a duplicate is found, returns None"""
    user = create_user(db, request.username)
    return UserSchema.model_validate(user)

@router.post("/get", response_model=UserSchema)
def get(db: DBSession, request: GetUserRequest) -> UserSchema | None:
    """Get a user from the username. If user not found, returns None"""
    
@router.post("/update_last_login", response_model=UserSchema)
def update_last_login(db: DBSession, request: UpdateUserLastLoginRequest) -> datetime | None:
    """Updates user with the given request info. If user not found, returns None"""
    return update_user_last_login(db, request.username, request.last_login)

@router.post("/update_activity", response_model=UserSchema)
def update_activity(db: DBSession, request: UpdateUserActivityRequest) -> datetime | None:
    """Updates user with the given request info. If user not found, returns None"""
    return update_user_activity(db, request.username, request.is_active)

@router.post("/delete", response_model=UserSchema)
def delete(db: DBSession, request: DeleteUserRequest) -> UserSchema | None:
    """Create and return new user account. If a duplicate is found, returns None"""
    user = delete_user(db, request.username)
    return UserSchema.model_validate(user)