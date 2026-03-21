
class InsufficientCoinsError(Exception):
    def __init__(self, user_id: object, required: int, available: int) -> None:
        self.user_id = user_id
        self.required = required
        self.available = available
        super().__init__(
            f"User '{user_id}' needs {required} DevCoins but only has {available}"
        )
