from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_customer_lookup_returns_matching_record() -> None:
    response = client.get("/customers/CUST-102")

    assert response.status_code == 200
    payload = response.json()
    assert payload["customer_id"] == "CUST-102"
    assert payload["entitlement_enabled"] is False


def test_unknown_customer_returns_404() -> None:
    response = client.get("/customers/CUST-999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Customer CUST-999 was not found."}


def test_valid_escalation_returns_created_record() -> None:
    payload = {
        "customer_id": "CUST-102",
        "issue": "Unable to access subscribed content",
        "finding": "Subscription is active but entitlement is disabled",
        "troubleshooting_performed": [
            "Verified customer account",
            "Verified subscription status",
            "Checked entitlement state",
        ],
    }

    response = client.post("/escalations", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "created"
    assert body["customer_id"] == "CUST-102"
    assert body["recommended_team"] == "Engineering"
    assert body["escalation_id"].startswith("ESC-")


def test_invalid_escalation_is_rejected() -> None:
    payload = {
        "customer_id": "CUST-102",
        "issue": "Unable to access subscribed content",
        "finding": "Subscription is active but entitlement is disabled",
    }

    response = client.post("/escalations", json=payload)

    assert response.status_code == 422
