from app.decision import Posture, decide


def test_clean_allows():
    assert decide("prod", Posture()).outcome == "allow"


def test_high_restricts():
    assert decide("prod", Posture(max_severity="high")).outcome == "restrict"


def test_critical_denies():
    assert decide("prod", Posture(max_severity="critical")).outcome == "deny"


def test_known_exploited_denies():
    assert decide("dev", Posture(known_exploited=True)).outcome == "deny"


def test_stale_prod_denies_but_dev_restricts():
    assert decide("prod", Posture(status="stale")).outcome == "deny"
    assert decide("dev", Posture(status="stale")).outcome == "restrict"


def test_remediation_never_denied():
    p = Posture(max_severity="critical", known_exploited=True)
    assert decide("prod", p, remediation=True).outcome == "restrict"