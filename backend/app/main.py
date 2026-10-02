from typing import Any

from fastapi import FastAPI, HTTPException
from langgraph.types import Command
from pydantic import BaseModel, Field

from .graph import graph
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

