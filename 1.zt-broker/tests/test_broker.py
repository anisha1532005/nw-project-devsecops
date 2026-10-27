import pytest

from app import broker
from app.decision import Posture

M = """
stage: deploy
environment: prod
actions: [s3:PutObject]
resources: ["arn:aws:s3:::bucket-x/*"]
max_duration_seconds: 300
intent: release
"""


def test_full_flow_and_decoy():
    r = broker.request_access(M, Posture())
    assert r["outcome"] == "allow"
    tok = r["broker_token"]

    c = broker.exchange(tok)
    assert c["_decoy"] is False
    assert broker.use(c["access_key"], "s3:PutObject") is True

    broker.complete(r["run_id"])
    assert broker.use(c["access_key"], "s3:PutObject") is False

    d = broker.exchange(tok, source="9.9.9.9")
    assert d["_decoy"] is True
    assert broker.use(d["access_key"], "s3:GetObject", source="9.9.9.9") is False
    assert broker.canaries[d["access_key"]]["hits"] == 1


def test_critical_is_denied():
    r = broker.request_access(M, Posture(max_severity="critical"))
    assert r["outcome"] == "deny"
    assert "broker_token" not in r


def test_unknown_token_rejected():
    with pytest.raises(PermissionError):
        broker.exchange("not-a-real-token")


def test_high_is_restricted_and_short():
    r = broker.request_access(M, Posture(max_severity="high"))
    assert r["outcome"] == "restrict"
    assert r["ttl"] <= 60