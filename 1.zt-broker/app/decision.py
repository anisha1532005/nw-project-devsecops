from pydantic import BaseModel


class Posture(BaseModel):
    status: str = "ok"            # ok, failed, stale
    max_severity: str = "none"    # none, medium, high, critical
    known_exploited: bool = False


class Decision(BaseModel):
    outcome: str                  # allow, restrict, deny
    reasons: list[str]


def decide(environment: str, posture: Posture, remediation: bool = False) -> Decision:
    prod = environment == "prod"

    if remediation:
        return Decision(outcome="restrict", reasons=["remediation deploy: restricted, never denied"])

    if posture.status in ("failed", "stale"):
        if prod:
            return Decision(outcome="deny", reasons=["assessment " + posture.status + " in prod: fail closed"])
        return Decision(outcome="restrict", reasons=["assessment " + posture.status + " in non-prod"])

    if posture.max_severity == "critical" or posture.known_exploited:
        return Decision(outcome="deny", reasons=["critical or known-exploited finding"])

    if posture.max_severity == "high":
        return Decision(outcome="restrict", reasons=["high severity finding"])

    return Decision(outcome="allow", reasons=["no findings above threshold"])