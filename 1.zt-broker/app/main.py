from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app import broker
from app.dashboard import PAGE
from app.decision import Posture
from app.store import read_audit

app = FastAPI(title="ZT Broker")


class AccessRequest(BaseModel):
    manifest: str
    posture: Posture = Posture()
    remediation: bool = False


class ExchangeRequest(BaseModel):
    token: str
    source: str = "unknown"


class UseRequest(BaseModel):
    access_key: str
    action: str
    source: str = "unknown"


class CompletionRequest(BaseModel):
    run_id: str
    status: str = "success"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/access-requests")
def access(req: AccessRequest):
    try:
        return broker.request_access(req.manifest, req.posture, req.remediation)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/v1/exchange")
def exchange(req: ExchangeRequest):
    try:
        creds = broker.exchange(req.token, req.source)
    except PermissionError:
        raise HTTPException(status_code=401, detail="invalid token")
    creds.pop("_decoy", None)  # attacker must not see which one is a decoy
    return creds


@app.post("/v1/use")
def use(req: UseRequest):
    if not broker.use(req.access_key, req.action, req.source):
        raise HTTPException(status_code=403, detail="AccessDenied")
    return {"result": "ok"}


@app.post("/v1/completions")
def completions(req: CompletionRequest):
    return broker.complete(req.run_id, req.status)


@app.post("/v1/reap")
def reap():
    return {"reaped": broker.reap()}


@app.get("/v1/audit")
def audit_log():
    return read_audit()


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return PAGE