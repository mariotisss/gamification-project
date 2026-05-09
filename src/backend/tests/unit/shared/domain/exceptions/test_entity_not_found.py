from __future__ import annotations

from uuid import uuid4

from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError


def test_given_entity_type_and_id_when_raised_then_message_includes_both() -> None:
    entity_id = uuid4()

    error = EntityNotFoundError(entity_type="Mission", entity_id=entity_id)

    assert "Mission" in str(error)
    assert str(entity_id) in str(error)
    assert error.entity_type == "Mission"
    assert error.entity_id == entity_id


def test_given_exception_when_caught_then_is_subclass_of_exception() -> None:
    assert issubclass(EntityNotFoundError, Exception)
