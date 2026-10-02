from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "HR Onboarding Concierge"

    print("PASS: /health")


def test_pending_approvals():
    response = client.get("/pending-approvals")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    print("PASS: /pending-approvals")


def test_approve_missing_thread():
    response = client.post(
        "/approve",
        json={
            "thread_id": "non-existent-thread",
        },
    )

    assert response.status_code == 404

    print("PASS: /approve rejects unknown thread")


def test_deny_missing_thread():
    response = client.post(
        "/deny",
        json={
            "thread_id": "non-existent-thread",
        },
    )

    assert response.status_code == 404

    print("PASS: /deny rejects unknown thread")


def test_edit_and_approve_missing_thread():
    response = client.post(
        "/edit-and-approve",
        json={
            "thread_id": "non-existent-thread",
            "employee_id": "EMP1002",
            "system": "PAYROLL",
        },
    )

    assert response.status_code == 404

    print("PASS: /edit-and-approve rejects unknown thread")


if __name__ == "__main__":
    test_health()
    test_pending_approvals()
    test_approve_missing_thread()
    test_deny_missing_thread()
    test_edit_and_approve_missing_thread()

    print()
    print("ALL FASTAPI API TESTS PASSED")