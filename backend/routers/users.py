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
    user = get_user(db, request.username)
    return UserSchema.model_validate(user)
    

@router.post("/update", response_model=UserSchema)
def update(db: DBSession, request: UpdateUserRequest) -> UserSchema | None:
    """Update user fields. If user not found, returns None"""
    user = update_user(db, request)
    return UserSchema.model_validate(user)

@router.post("/delete", response_model=UserSchema)
def delete(db: DBSession, request: DeleteUserRequest) -> UserSchema | None:
    """Create and return new user account. If a duplicate is found, returns None"""
    user = delete_user(db, request.username)
    return UserSchema.model_validate(user)