from pydantic import BaseModel
from uuid import UUID

class CreateRewardRequest(BaseModel):
    name: str
    description: str
    cost: int
    reward_type: str

class RewardResponse(BaseModel):
    id: str
    name: str
    description: str
    cost: int
    reward_type: str

class PurchaseRewardRequest(BaseModel):
    user_id: UUID
