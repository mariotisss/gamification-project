from __future__ import annotations

from uuid import UUID, uuid4

from core.pkg.reward_system.domain.entities.reward import Reward


def test_given_reward_fields_when_instantiated_then_defaults_id() -> None:
    reward = Reward(name="N", description="D", cost=10, reward_type="cosmetic")

    assert isinstance(reward.id, UUID)


def test_given_explicit_id_when_instantiated_then_keeps_provided_id() -> None:
    explicit_id = uuid4()

    reward = Reward(
        name="N",
        description="D",
        cost=10,
        reward_type="cosmetic",
        id=explicit_id,
    )

    assert reward.id == explicit_id
