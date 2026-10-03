import json
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from langchain_google_genai.chat_models import GoogleRateLimitError

from backend.app import main


client = TestClient(main.app)
EXPECTED_THREAD_ID = "demo-phase3-002"
EXPECTED_QUESTION = "Which documents are required for a new employee onboarding?"


def _mock_run_state():
    return {
        "category": "PAPERWORK",
        "response": "New employees should provide identity and tax forms.",
        "approval_required": False,
        "approval_status": "NOT_REQUIRED",
        "approval_id": "",
        "write_draft": {},
        "write_result": "",
        "messages": [object()],
    }


def test_run_validation():
    empty_question = client.post(
        "/run",
        json={"question": "", "thread_id": "validation-thread"},
    )
    empty_thread_id = client.post(
        "/run",
        json={"question": "A valid question", "thread_id": ""},
    )

    assert empty_question.status_code == 422
    assert empty_thread_id.status_code == 422


def test_run_returns_successful_json_state():
    with patch.object(main, "run_ticket", return_value=_mock_run_state()):
        response = client.post(
            "/run",
            json={"question": EXPECTED_QUESTION, "thread_id": EXPECTED_THREAD_ID},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["thread_id"] == EXPECTED_THREAD_ID
    assert data["question"] == EXPECTED_QUESTION
    assert data["category"] == "PAPERWORK"
    assert data["response"] == "New employees should provide identity and tax forms."
    assert data["approval_required"] is False
    assert data["approval_status"] == "NOT_REQUIRED"
    assert data["write_draft"] == {}
    assert data["write_result"] == ""
    assert "messages" not in data


def test_run_calls_existing_ticket_with_expected_arguments():
    with patch.object(main, "run_ticket", return_value=_mock_run_state()) as run_ticket:
        response = client.post(
            "/run",
            json={"question": EXPECTED_QUESTION, "thread_id": EXPECTED_THREAD_ID},
        )

    assert response.status_code == 200
    run_ticket.assert_called_once_with(EXPECTED_QUESTION, EXPECTED_THREAD_ID)


def test_run_returns_useful_json_for_gemini_quota_error():
    with patch.object(main, "run_ticket", side_effect=GoogleRateLimitError("mock quota")):
        response = client.post(
            "/run",
            json={"question": EXPECTED_QUESTION, "thread_id": EXPECTED_THREAD_ID},
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": (
            "The Gemini request quota is exhausted. Check the configured "
            "Gemini project quota and retry when capacity is available."
        )
    }


def test_stream_sse_safe_serialization():
    streamed_state = {
        "category": "PAYROLL",
        "response": "Done",
        "approval_required": False,
        "approval_status": "NONE",
        "approval_id": "",
        "write_draft": {},
        "write_result": "",
        "iteration_count": 2,
        "escalated": False,
        "messages": [object()],
    }
    with patch.object(main, "stream_ticket", return_value=iter([streamed_state])):
        response = client.post(
            "/stream",
            json={"question": "Pay date?", "thread_id": "thread-b"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    line = next(line for line in response.text.splitlines() if line.startswith("data: "))
    data = json.loads(line[6:])
    assert data["category"] == "PAYROLL"
    assert data["iteration_count"] == 2
    assert "messages" not in data


def test_root_serves_ui_and_frontend_uses_single_safe_body_read():
    response = client.get("/")
    frontend = Path(main.FRONTEND_DIR, "index.html").read_text(encoding="utf-8")
    api_helper = frontend.split("async function api(path, body) {", 1)[1].split("\n}", 1)[0]

    assert response.status_code == 200
    assert "HR Onboarding Concierge" in response.text
    assert "Edit &amp; Approve" in response.text
    assert api_helper.count("response.text()") == 1
    assert "response.json()" not in api_helper
    assert "JSON.parse(text)" in api_helper
    assert "if (!response.ok)" in api_helper
    assert "text.trim()" in api_helper
    assert "empty or invalid JSON response" in api_helper


if __name__ == "__main__":
    test_run_validation()
    test_run_returns_successful_json_state()
    test_run_calls_existing_ticket_with_expected_arguments()
    test_run_returns_useful_json_for_gemini_quota_error()
    test_stream_sse_safe_serialization()
    test_root_serves_ui_and_frontend_uses_single_safe_body_read()
    print("ALL PHASE 3 API/UI TESTS PASSED")
