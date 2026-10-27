import pytest
from app.manifest import load_manifest

GOOD = """
stage: deploy
environment: prod
actions: [s3:PutObject]
resources: ["arn:aws:s3:::bucket-x/*"]
max_duration_seconds: 300
intent: release
"""


def test_good_manifest():
    assert load_manifest(GOOD).stage == "deploy"


def test_wildcard_action_rejected():
    with pytest.raises(ValueError):
        load_manifest(GOOD.replace("s3:PutObject", "s3:*"))


def test_wildcard_resource_rejected():
    with pytest.raises(ValueError):
        load_manifest(GOOD.replace("arn:aws:s3:::bucket-x/*", "*"))


def test_too_long_rejected():
    with pytest.raises(ValueError):
        load_manifest(GOOD.replace("300", "5000"))