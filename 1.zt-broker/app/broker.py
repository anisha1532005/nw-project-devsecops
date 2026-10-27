import hashlib
import secrets
import time

from app.cloud import FakeCloud
from app.decision import Posture, decide
from app.manifest import load_manifest
from app.store import audit

cloud = FakeCloud()
tokens = {}     # token hash -> record
canaries = {}   # decoy access key -> record


def _h(t):
    return hashlib.sha256(t.encode()).hexdigest()


def request_access(manifest_text, posture, remediation=False):
    m = load_manifest(manifest_text)
    run_id = secrets.token_hex(4)
    d = decide(m.environment, posture, remediation)
    audit("decision", run_id=run_id, outcome=d.outcome, reasons=d.reasons)
    if d.outcome == "deny":
        return {"run_id": run_id, "outcome": "deny", "reasons": d.reasons}

    ttl = m.max_duration_seconds
    actions = m.actions
    if d.outcome == "restrict":
        ttl = min(ttl, 60)
        actions = [a for a in actions if not a.startswith("iam:")]

    token = secrets.token_urlsafe(24)
    tokens[_h(token)] = {
        "run_id": run_id,
        "state": "active",
        "expires": time.time() + ttl,
        "actions": actions,
        "resources": m.resources,
    }
    audit("token_issued", run_id=run_id, ttl=ttl, outcome=d.outcome)
    return {
        "run_id": run_id,
        "outcome": d.outcome,
        "reasons": d.reasons,
        "broker_token": token,
        "ttl": ttl,
    }


def exchange(token, source="unknown"):
    rec = tokens.get(_h(token))
    if rec is None:
        audit("unknown_token", source=source)
        raise PermissionError("invalid token")

    now = time.time()
    if rec["state"] == "active" and rec["expires"] > now:
        creds = cloud.issue(rec["run_id"], rec["actions"], rec["resources"], int(rec["expires"] - now))
        audit("exchange", run_id=rec["run_id"], source=source)
        creds["_decoy"] = False
        return creds

    # revoked or expired token came back: give a decoy
    rec["state"] = "expired" if rec["state"] == "active" else rec["state"]
    cid = secrets.token_hex(6)
    key = "AKIA" + secrets.token_hex(8).upper()
    canaries[key] = {"correlation_id": cid, "hits": 0}
    audit("DECOY_ISSUED", correlation_id=cid, run_id=rec["run_id"], source=source)
    return {"access_key": key, "secret": secrets.token_hex(16), "expires_in": 300, "_decoy": True}


def use(access_key, action, source="unknown"):
    c = canaries.get(access_key)
    if c:
        c["hits"] += 1
        audit("DECOY_HIT", correlation_id=c["correlation_id"], action=action, source=source)
        return False
    ok = cloud.is_valid(access_key)
    audit("credential_use", valid=ok, action=action)
    return ok


def complete(run_id, status="success"):
    t0 = time.time()
    n = 0
    for rec in tokens.values():
        if rec["run_id"] == run_id and rec["state"] == "active":
            rec["state"] = "revoked"
            n += 1
    cloud.revoke(run_id)
    audit("revoked", run_id=run_id, status=status, tokens=n, seconds=round(time.time() - t0, 4))
    return {"revoked": n}


def reap():
    now = time.time()
    n = 0
    for rec in tokens.values():
        if rec["state"] == "active" and rec["expires"] <= now:
            rec["state"] = "expired"
            cloud.revoke(rec["run_id"])
            n += 1
    if n:
        audit("reaped", count=n)
    return n