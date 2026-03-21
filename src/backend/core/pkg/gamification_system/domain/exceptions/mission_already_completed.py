
class MissionAlreadyCompletedError(Exception):
    def __init__(self, user_id: object, mission_id: object) -> None:
        self.user_id = user_id
        self.mission_id = mission_id
        super().__init__(
            f"User '{user_id}' has already completed mission '{mission_id}'"
        )
