import json
from pathlib import Path
from typing import Any, Iterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_google_genai.chat_models import GoogleRateLimitError
from langgraph.types import Command
from pydantic import BaseModel, Field

from .graph import graph, run_ticket, stream_ticket
from .persistence import checkpointer
from .forensics import (
    apply_correction,
    find_bad_checkpoint,
    state_forensics,
    time_travel,
)

app = FastAPI(
    title="HR Onboarding Concierge",
    version="1.0.0",
)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class RunRequest(BaseModel):
    question: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)


@app.get("/")
def index():
    from fastapi.responses import FileResponse
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/run")
def run(request: RunRequest) -> dict[str, Any]:
    try:
        state = run_ticket(request.question, request.thread_id)
    except GoogleRateLimitError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "The Gemini request quota is exhausted. Check the configured "
                "Gemini project quota and retry when capacity is available."
            ),
        ) from exc
    keys = ("category", "response", "approval_required", "approval_status",
            "approval_id", "write_draft", "write_result")
    return {"thread_id": request.thread_id, "question": request.question,
            **{key: state.get(key) for key in keys}}


_STREAM_FIELDS = ("category", "response", "approval_required", "approval_status",
                  "approval_id", "write_draft", "write_result", "iteration_count", "escalated")


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): converted for k, v in value.items()
                if (converted := _json_safe(v)) is not _UNSERIALIZABLE}
    if isinstance(value, (list, tuple)):
        return [converted for item in value
                if (converted := _json_safe(item)) is not _UNSERIALIZABLE]
    return _UNSERIALIZABLE


_UNSERIALIZABLE = object()


def serialize_stream_state(state: dict[str, Any]) -> dict[str, Any]:
    serialized = {}
    for key in _STREAM_FIELDS:
        value = _json_safe(state.get(key))
        if value is _UNSERIALIZABLE:
            value = None
        serialized[key] = value
    return serialized


@app.post("/stream")
def stream(request: RunRequest) -> StreamingResponse:
    def events() -> Iterator[str]:
        for state in stream_ticket(request.question, request.thread_id):
            payload = serialize_stream_state(state)
            payload.update(thread_id=request.thread_id, question=request.question)
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream")


class ApprovalRequest(BaseModel):
    thread_id: str = Field(min_length=1)


class EditApprovalRequest(BaseModel):
    thread_id: str = Field(min_length=1)
    employee_id: str = Field(min_length=1)
    system: str = Field(min_length=1)

class ForensicsRequest(BaseModel):
    thread_id: str = Field(min_length=1)


class FindBadCheckpointRequest(BaseModel):
    thread_id: str = Field(min_length=1)
    field: str = Field(min_length=1)
    bad_value: Any


class ApplyCorrectionRequest(BaseModel):
    thread_id: str = Field(min_length=1)
    checkpoint_config: dict[str, Any]
    updates: dict[str, Any]


class TimeTravelRequest(BaseModel):
    thread_id: str = Field(min_length=1)
    checkpoint_id: str = Field(min_length=1)

@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "HR Onboarding Concierge",
    }


@app.get("/pending-approvals")
def pending_approvals() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    for checkpoint in checkpointer.list(None, limit=1000):
        values = checkpoint.checkpoint.get("channel_values", {})

        if not values.get("approval_required", False):
            continue

        if values.get("approval_status", "").upper() != "PENDING":
            continue

        results.append(
            {
                "thread_id": checkpoint.config["configurable"]["thread_id"],
                "approval_id": values.get("approval_id", ""),
                "approval_request": values.get(
                    "approval_request",
                    {},
                ),
            }
        )

    return results

@app.post("/forensics")
def get_forensics(request: ForensicsRequest) -> dict[str, Any]:
    try:
        timeline = state_forensics(request.thread_id)
        return {
            "thread_id": request.thread_id,
            "timeline": timeline,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/forensics/find-bad-checkpoint")
def find_bad_checkpoint_endpoint(
    request: FindBadCheckpointRequest,
) -> dict[str, Any]:
    try:
        result = find_bad_checkpoint(
            request.thread_id,
            request.field,
            request.bad_value,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="No checkpoint containing the requested bad value was found.",
            )

        return result

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/forensics/apply-correction")
def apply_correction_endpoint(
    request: ApplyCorrectionRequest,
) -> dict[str, Any]:
    try:
        return apply_correction(
            request.thread_id,
            request.checkpoint_config,
            request.updates,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/forensics/time-travel")
def time_travel_endpoint(
    request: TimeTravelRequest,
) -> dict[str, Any]:
    try:
        return time_travel(
            request.thread_id,
            request.checkpoint_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
def resume_approval(
    thread_id: str,
    resume_value: dict[str, Any],
) -> dict[str, Any]:
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    snapshot = graph.get_state(config)

    if not snapshot.values:
        raise HTTPException(
            status_code=404,
            detail=f"No graph state found for thread_id: {thread_id}",
        )

    approval_required = snapshot.values.get(
        "approval_required",
        False,
    )

    approval_status = snapshot.values.get(
        "approval_status",
        "",
    ).upper()

    if not approval_required:
        raise HTTPException(
            status_code=400,
            detail="This thread does not have a pending approval.",
        )

    if approval_status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=(
                "Approval is no longer pending. "
                f"Current status: {approval_status}"
            ),
        )

    result = graph.invoke(
        Command(resume=resume_value),
        config=config,
    )

    return {
        "thread_id": thread_id,
        "approval_status": result.get(
            "approval_status",
            "",
        ),
        "response": result.get(
            "response",
            "",
        ),
        "write_result": result.get(
            "write_result",
            "",
        ),
    }


@app.post("/approve")
def approve(request: ApprovalRequest) -> dict[str, Any]:
    return resume_approval(
        request.thread_id,
        {
            "status": "APPROVED",
        },
    )


@app.post("/deny")
def deny(request: ApprovalRequest) -> dict[str, Any]:
    return resume_approval(
        request.thread_id,
        {
            "status": "DENIED",
        },
    )


@app.post("/edit-and-approve")
def edit_and_approve(
    request: EditApprovalRequest,
) -> dict[str, Any]:
    return resume_approval(
        request.thread_id,
        {
            "status": "EDIT_AND_APPROVE",
            "employee_id": request.employee_id,
            "system": request.system,
        },
    )

