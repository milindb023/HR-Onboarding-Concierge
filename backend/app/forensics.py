from typing import Any

from .graph import graph


def _get_thread_config(thread_id: str) -> dict[str, Any]:
    return {
        "configurable": {
            "thread_id": thread_id,
        }
    }


def _get_anomaly_flags(
    values: dict[str, Any],
    next_nodes: tuple[str, ...],
) -> list[str]:
    flags: list[str] = []

    # A terminal state should normally have a response.
    # This identifies a suspicious terminal checkpoint.
    if not next_nodes:
        response = str(values.get("response", "")).strip()

        if not response:
            flags.append("EMPTY_RESPONSE")

    # A graph that remains pointed at the same active node can indicate
    # that it is approaching a loop.
    if len(next_nodes) == 1:
        current_node = next_nodes[0]

        if current_node == "agent":
            iteration_count = values.get("iteration_count", 0)

            if iteration_count >= 2:
                flags.append("LOOP_PROXIMITY")

        if current_node == "approval_interrupt":
            approval_status = str(
                values.get("approval_status", "")
            ).strip().upper()

            if approval_status == "PENDING":
                flags.append("APPROVAL_PENDING")

    # Guardrail state is explicitly visible in the checkpoint.
    if values.get("guardrail_blocked", False):
        flags.append("GUARDRAIL_BLOCKED")

    return flags


def state_forensics(thread_id: str) -> list[dict[str, Any]]:
    """
    Walk the persisted checkpoint history for a thread and return
    a chronological forensic timeline.

    The original checkpoints are read only. No graph state is changed.
    """

    if not thread_id.strip():
        raise ValueError("thread_id is required")

    config = _get_thread_config(thread_id)

    snapshots = list(
        graph.get_state_history(config)
    )

    timeline: list[dict[str, Any]] = []

    for index, snapshot in enumerate(snapshots):
        values = dict(snapshot.values or {})

        snapshot_config = snapshot.config.get(
            "configurable",
            {},
        )

        parent_config = snapshot.parent_config or {}

        parent_configurable = parent_config.get(
            "configurable",
            {},
        )

        next_nodes = tuple(snapshot.next or ())

        timeline.append(
            {
                "sequence": index,
                "checkpoint_id": snapshot_config.get(
                    "checkpoint_id",
                    "",
                ),
                "parent_checkpoint_id": parent_configurable.get(
                    "checkpoint_id",
                    "",
                ),
                "thread_id": snapshot_config.get(
                    "thread_id",
                    thread_id,
                ),
                "next": list(next_nodes),
                "step": snapshot.metadata.get(
                    "step",
                    None,
                ),
                "source": snapshot.metadata.get(
                    "source",
                    "",
                ),
                "iteration_count": values.get(
                    "iteration_count",
                    0,
                ),
                "category": values.get(
                    "category",
                    "",
                ),
                "approval_status": values.get(
                    "approval_status",
                    "",
                ),
                "guardrail_blocked": values.get(
                    "guardrail_blocked",
                    False,
                ),
                "response_present": bool(
                    str(
                        values.get(
                            "response",
                            "",
                        )
                    ).strip()
                ),
                "anomaly_flags": _get_anomaly_flags(
                    values,
                    next_nodes,
                ),
            }
        )

    return timeline

def find_bad_checkpoint(
    thread_id: str,
    field: str,
    bad_value: Any,
) -> dict[str, Any] | None:
    """
    Find the checkpoint where a state field contains the bad value.

    Returns the checkpoint containing the bad value together with the
    parent configuration that represents the state immediately before
    that checkpoint was created.
    """
    if not thread_id.strip():
        raise ValueError("thread_id is required")

    if not field.strip():
        raise ValueError("field is required")

    config = _get_thread_config(thread_id)

    for snapshot in graph.get_state_history(config):
        values = dict(snapshot.values or {})

        if values.get(field) != bad_value:
            continue

        checkpoint_config = snapshot.config
        parent_config = snapshot.parent_config

        return {
            "thread_id": thread_id,
            "field": field,
            "bad_value": bad_value,
            "checkpoint_id": (
                checkpoint_config
                .get("configurable", {})
                .get("checkpoint_id", "")
            ),
            "checkpoint_config": checkpoint_config,
            "parent_config": parent_config,
            "parent_checkpoint_id": (
                parent_config
                .get("configurable", {})
                .get("checkpoint_id", "")
                if parent_config
                else ""
            ),
            "state": values,
        }

    return None


def apply_correction(
    thread_id: str,
    checkpoint_config: dict[str, Any],
    updates: dict[str, Any],
) -> dict[str, Any]:
    """
    Apply a state correction using LangGraph update_state().

    This does not modify SQLite directly. LangGraph creates a new
    checkpoint containing the corrected state.
    """
    if not thread_id.strip():
        raise ValueError("thread_id is required")

    if not updates:
        raise ValueError("updates must not be empty")

    configurable = checkpoint_config.get("configurable", {})

    checkpoint_thread_id = configurable.get("thread_id", "")
    checkpoint_id = configurable.get("checkpoint_id", "")

    if checkpoint_thread_id != thread_id:
        raise ValueError(
            "checkpoint_config thread_id does not match thread_id"
        )

    if not checkpoint_id:
        raise ValueError(
            "checkpoint_config must contain checkpoint_id"
        )

    new_config = graph.update_state(
        checkpoint_config,
        updates,
    )

    new_checkpoint_id = (
        new_config
        .get("configurable", {})
        .get("checkpoint_id", "")
    )

    return {
        "thread_id": thread_id,
        "previous_checkpoint_id": checkpoint_id,
        "new_checkpoint_id": new_checkpoint_id,
        "updates": updates,
    }

def time_travel(
    thread_id: str,
    checkpoint_id: str,
) -> dict[str, Any]:
    """
    Re-run the graph from a historical checkpoint.

    The original checkpoint history is preserved. LangGraph creates
    a new branch from the selected checkpoint.
    """
    if not thread_id.strip():
        raise ValueError("thread_id is required")

    if not checkpoint_id.strip():
        raise ValueError("checkpoint_id is required")

    config = {
        "configurable": {
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
        }
    }

    snapshot = graph.get_state(config)

    if not snapshot.values:
        raise ValueError(
            f"No checkpoint found for thread_id={thread_id}, "
            f"checkpoint_id={checkpoint_id}"
        )

    result = graph.invoke(
        None,
        config=config,
    )

    final_snapshot = graph.get_state(
        {
            "configurable": {
                "thread_id": thread_id,
            }
        }
    )

    new_checkpoint_id = (
        final_snapshot.config
        .get("configurable", {})
        .get("checkpoint_id", "")
    )

    return {
        "thread_id": thread_id,
        "source_checkpoint_id": checkpoint_id,
        "new_checkpoint_id": new_checkpoint_id,
        "response": result.get("response", ""),
        "state": dict(final_snapshot.values or {}),
    }




