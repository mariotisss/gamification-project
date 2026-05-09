from __future__ import annotations

from uuid import UUID, uuid4

from core.pkg.mission_system.domain.entities.mission import Mission


def test_given_mission_fields_when_instantiated_then_defaults_id_and_is_active() -> None:
    mission = Mission(
        title="Title",
        description="Desc",
        xp_reward=10,
        coin_reward=5,
    )

    assert isinstance(mission.id, UUID)
    assert mission.is_active is True


def test_given_explicit_id_when_instantiated_then_keeps_provided_id() -> None:
    explicit_id = uuid4()

    mission = Mission(
        title="Title",
        description="Desc",
        xp_reward=10,
        coin_reward=5,
        id=explicit_id,
    )

    assert mission.id == explicit_id


def test_given_two_missions_when_instantiated_then_ids_are_unique() -> None:
    mission_a = Mission(title="A", description="a", xp_reward=1, coin_reward=1)
    mission_b = Mission(title="B", description="b", xp_reward=1, coin_reward=1)

    assert mission_a.id != mission_b.id
