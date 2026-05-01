from pydantic import BaseModel
from uuid import UUID

class CreateMissionRequest(BaseModel):
    title: str
    description: str
    xp_reward: int
    coin_reward: int

class MissionResponse(BaseModel):
    id: str
    title: str
    description: str
    xp_reward: int
    coin_reward: int
    is_active: bool

class CompleteMissionRequest(BaseModel):
    user_id: UUID

class MissionCompletionResponse(BaseModel):
    id: str
    user_id: str
    mission_id: str
    completed_at: str
