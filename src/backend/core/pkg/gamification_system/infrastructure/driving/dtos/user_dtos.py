from pydantic import BaseModel
from uuid import UUID

class CreateUserRequest(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    xp: int
    level: int
    dev_coins: int
    created_at: str

    model_config = {"from_attributes": True}
