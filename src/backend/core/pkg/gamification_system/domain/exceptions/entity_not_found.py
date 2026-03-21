
class EntityNotFoundError(Exception):
    def __init__(self, entity_type: str, entity_id: object) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id '{entity_id}' not found")
