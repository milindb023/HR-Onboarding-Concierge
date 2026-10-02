from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def main() -> None:
    # ---------------------------------------------------------
    # 1. /forensics
    # ---------------------------------------------------------
    response = client.post(
        "/forensics",
        json={
            "thread_id": "step11c-deny-thread",
        },
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["thread_id"] == "step11c-deny-thread"
    assert isinstance(body["timeline"], list)

    print("PASS: POST /forensics")


    # ---------------------------------------------------------
    # 2. /forensics/find-bad-checkpoint
    # ---------------------------------------------------------
    response = client.post(
        "/forensics/find-bad-checkpoint",
        json={
            "thread_id": "step11c-deny-thread",
            "field": "approval_status",
            "bad_value": "DENIED",
        },
    )

    assert response.status_code == 404, response.text

    print("PASS: /forensics/find-bad-checkpoint handles missing checkpoint")


    # ---------------------------------------------------------
    # 3. Validation
    # ---------------------------------------------------------
    response = client.post(
        "/forensics",
        json={
            "thread_id": "",
        },
    )

    assert response.status_code == 422, response.text

    print("PASS: /forensics validates thread_id")


    # ---------------------------------------------------------
    # 4. Time-travel validation
    # ---------------------------------------------------------
    response = client.post(
        "/forensics/time-travel",
        json={
            "thread_id": "step11c-deny-thread",
            "checkpoint_id": "does-not-exist",
        },
    )

    assert response.status_code == 400, response.text

    print("PASS: /forensics/time-travel rejects unknown checkpoint")


    print()
    print("==============================================")
    print("ALL FASTAPI FORENSICS TESTS PASSED")
    print("==============================================")


if __name__ == "__main__":
    main()