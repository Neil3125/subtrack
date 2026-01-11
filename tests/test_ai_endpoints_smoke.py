from fastapi.testclient import TestClient

from app.main import app
from init_auth import init_auth


def login(client: TestClient):
    init_auth()
    resp = client.post("/login", data={"username": "admin", "password": "admin"}, follow_redirects=False)
    assert resp.status_code in (302, 303)


def test_ai_status_returns_html_when_authenticated():
    client = TestClient(app)
    login(client)

    resp = client.get("/api/ai/status")
    assert resp.status_code == 200
    assert "ai-status-badge" in resp.text


def test_extract_from_url_accepts_json_and_form():
    client = TestClient(app)
    login(client)

    resp_json = client.post("/api/ai/extract-from-url", json={"url": "https://example.com/pricing"})
    assert resp_json.status_code == 200

    resp_form = client.post("/api/ai/extract-from-url", data={"url": "https://example.com/pricing"})
    assert resp_form.status_code == 200


def test_categorize_subscription_accepts_json_and_form():
    client = TestClient(app)
    login(client)

    resp_json = client.post(
        "/api/ai/categorize-subscription",
        json={"vendor_name": "Adobe", "plan_name": "Creative Cloud"},
    )
    assert resp_json.status_code == 200

    resp_form = client.post(
        "/api/ai/categorize-subscription",
        data={"vendor_name": "Adobe", "plan_name": "Creative Cloud"},
    )
    assert resp_form.status_code == 200
