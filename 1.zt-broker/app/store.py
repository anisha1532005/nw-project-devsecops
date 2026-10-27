import json
import threading
import time
from pathlib import Path

AUDIT_FILE = Path("audit.log")
_lock = threading.Lock()


def audit(event, **data):
    rec = {"ts": time.time(), "event": event, **data}
    with _lock:
        with AUDIT_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    return rec


def read_audit(limit=200):
    if not AUDIT_FILE.exists():
        return []
    lines = AUDIT_FILE.read_text(encoding="utf-8").splitlines()
    return [json.loads(x) for x in lines[-limit:]]