"""RITHM P24: exact synthetic receipt-to-human-response welfare example.

This reuses Wijayaratna et al. (2017) COST GEOMETRY only.
Receipt events and individual responses here are entirely constructed.
"""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ObservationAccess:
    measurement_end: int
    receipt_time: int
    decision_time: int
    version_valid: bool = True

    def authorized(self) -> bool:
        return self.version_valid and self.measurement_end <= self.receipt_time <= self.decision_time


@dataclass(frozen=True)
class Group:
    ab: int
    acb: int
    acd: int
    incident: int = 0

    def __post_init__(self):
        if any(type(x) is not int for x in (self.ab, self.acb, self.acd, self.incident)):
            raise TypeError("integer state required")
        if min(self.ab, self.acb, self.acd) < 0 or self.ab + self.acb + self.acd != 12:
            raise ValueError("12 nonnegative travelers required")
        if self.incident not in (0, 1):
            raise ValueError("binary incident required")

    def group_cost(self) -> int:
        n1, n2, n3, z = self.ab, self.acb, self.acd, self.incident
        return n1 * (10 + n1 + n2) + n2 * (13 + n2 + 19*z) + n3 * (22 - n1)

    def upstream_ac_sensor(self) -> int:
        """Hypothetical A-C total, NOT observed Seoul sensor data."""
        return self.acb + self.acd

    def switch_at_c(self, before: Literal["ACB", "ACD"], after: Literal["ACB", "ACD"]) -> "Group":
        if before == after:
            return self
        if before == "ACB" and after == "ACD" and self.acb > 0:
            return Group(self.ab, self.acb - 1, self.acd + 1, self.incident)
        if before == "ACD" and after == "ACB" and self.acd > 0:
            return Group(self.ab, self.acb + 1, self.acd - 1, self.incident)
        raise ValueError("only an eligible C-branch traveler can switch")


def policy_world(base: Group, access: ObservationAccess, response: str) -> Group:
    """All three worlds share the same toy receipt/advice, not the behavior."""
    if response not in ("no_change", "to_acb", "to_acd"):
        raise ValueError("unknown response")
    if not access.authorized() or response == "no_change":
        return base
    if response == "to_acb":
        return base.switch_at_c("ACD", "ACB")
    return base.switch_at_c("ACB", "ACD")


def one_switch_identified_set(base: Group, access: ObservationAccess) -> dict:
    worlds = {r: policy_world(base, access, r) for r in ("no_change", "to_acd", "to_acb")}
    assert len({g.upstream_ac_sensor() for g in worlds.values()}) == 1
    gains = {name: base.group_cost() - g.group_cost() for name, g in worlds.items()}
    return {"baseline_cost": base.group_cost(), "upstream_sensor_all_worlds": base.upstream_ac_sensor(),
            "possible_policy_costs": {name: g.group_cost() for name, g in worlds.items()},
            "possible_social_cost_improvement": gains,
            "sharp_improvement_interval": [min(gains.values()), max(gains.values())],
            "source_authority": "SYNTHETIC RECEIPT AND BEHAVIOR; ORIGINAL 2017 COST EQUATION ONLY"}


def witness() -> dict:
    base = Group(4, 4, 4, incident=0)
    ok = ObservationAccess(0, 1, 2)
    missing = ObservationAccess(0, 3, 2)
    result = one_switch_identified_set(base, ok)
    result["when_not_received"] = one_switch_identified_set(base, missing)
    return result


if __name__ == "__main__":
    import json
    print(json.dumps(witness(), indent=2, sort_keys=True))
