from pydantic import BaseModel
from datetime import datetime

class _UsernameRequest(BaseModel):
    username: str

class CreateUserRequest(_UsernameRequest):
    pass
    
class DeleteUserRequest(_UsernameRequest):
    pass

class GetUserRequest(_UsernameRequest):
    pass


class UpdateUserRequest(_UsernameRequest):
    last_login: datetime | None = None
    is_active: bool | None = None
    timezone: str | None = None
    theme: str | None = None