import sys, os
sys.path.append(os.getcwd())
try:
    from fastapi.testclient import TestClient
    from app.main import app
    import json

    client = TestClient(app)

    # Test service check
    resp = client.post("/api/log-check/generate", json={
        "check_type": "service",
        "mode": "automatic",
        "hours": 0,
        "minutes": 30
    })
    print("Service check response:", resp.status_code, resp.text)

    # Test manual check with am/pm
    resp = client.post("/api/log-check/generate", json={
        "check_type": "service",
        "mode": "manual",
        "start_time": "10:30 AM",
        "end_time": "11:00 AM",
        "date_str": "02/27/2026"
    })
    print("Manual check response:", resp.status_code, resp.text)
except Exception as e:
    import traceback
    traceback.print_exc()
