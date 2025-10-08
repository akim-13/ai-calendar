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

class UpdateUserLastLoginRequest(_UsernameRequest):
    last_login: datetime
    
class UpdateUserActivityRequest(_UsernameRequest):
    is_active: bool