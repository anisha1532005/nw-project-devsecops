import yaml
from pydantic import BaseModel, field_validator


class Manifest(BaseModel):
    stage: str
    environment: str
    actions: list[str]
    resources: list[str]
    max_duration_seconds: int
    intent: str = ""

    @field_validator("actions")
    @classmethod
    def check_actions(cls, v):
        if not v:
            raise ValueError("actions is empty")
        for a in v:
            if a == "*" or a.endswith(":*"):
                raise ValueError("wildcard action not allowed: " + a)
        return v

    @field_validator("resources")
    @classmethod
    def check_resources(cls, v):
        if not v:
            raise ValueError("resources is empty")
        for r in v:
            if r == "*" or r.endswith(":*"):
                raise ValueError("wildcard resource not allowed: " + r)
        return v

    @field_validator("max_duration_seconds")
    @classmethod
    def check_time(cls, v):
        if v < 1 or v > 900:
            raise ValueError("duration must be 1 to 900 seconds")
        return v


def load_manifest(text: str) -> Manifest:
    return Manifest(**yaml.safe_load(text))