from __future__ import annotations

from uuid import uuid4

from core.pkg.mission_system.domain.exceptions.mission_already_completed import (
    MissionAlreadyCompletedError,
)


def test_given_user_and_mission_when_raised_then_message_contains_both_ids() -> None:
    user_id = uuid4()
    mission_id = uuid4()

    error = MissionAlreadyCompletedError(user_id=user_id, mission_id=mission_id)

    assert str(user_id) in str(error)
    assert str(mission_id) in str(error)
    assert error.user_id == user_id
    assert error.mission_id == mission_id


def test_given_exception_when_caught_then_is_subclass_of_exception() -> None:
    assert issubclass(MissionAlreadyCompletedError, Exception)
