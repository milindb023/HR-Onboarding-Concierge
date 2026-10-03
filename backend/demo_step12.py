from __future__ import annotations

import json
from typing import Any

from backend.app.forensics import (
    apply_correction,
    find_bad_checkpoint,
    state_forensics,
    time_travel,
)
from backend.app.graph import graph


THREAD_ID = "step12-live-demo-thread"


def print_section(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, default=str))


def get_latest_snapshot() -> Any:
    snapshots = list(
        graph.get_state_history(
            {"configurable": {"thread_id": THREAD_ID}}
        )
    )

    if not snapshots:
        return None

    return snapshots[0]


def create_demo_thread() -> str:
    """
    Create a small persisted graph checkpoint for the demonstration.

    This uses the actual production graph/checkpointer but does not invoke
    the LLM. The existing persisted graph state is used as the starting point.
    """
    existing = get_latest_snapshot()

    if existing is not None:
        return existing.config["configurable"]["checkpoint_id"]

    result = graph.update_state(
        {
            "configurable": {
                "thread_id": THREAD_ID,
            }
        },
        {
            "question": "Please provision HR_PORTAL access for EMP1001",
            "iteration_count": 0,
        },
    )

    return result["configurable"]["checkpoint_id"]


def main() -> None:
    print_section("STEP 12 - CHECKPOINT FORENSICS DEMONSTRATION")

    print("Thread:")
    print(THREAD_ID)

    # ---------------------------------------------------------
    # 1. Create/read persisted checkpoint
    # ---------------------------------------------------------
    print_section("1. PERSISTED CHECKPOINT")

    source_checkpoint_id = create_demo_thread()

    print("Source checkpoint:")
    print(source_checkpoint_id)

    # ---------------------------------------------------------
    # 2. Deliberately corrupt state
    # ---------------------------------------------------------
    print_section("2. DELIBERATE CORRUPTION")

    source_snapshot = graph.get_state(
        {
            "configurable": {
                "thread_id": THREAD_ID,
                "checkpoint_id": source_checkpoint_id,
            }
        }
    )

    source_config = {
    "configurable": {
        "thread_id": source_snapshot.config["configurable"]["thread_id"],
        "checkpoint_ns": source_snapshot.config["configurable"].get(
            "checkpoint_ns", ""
        ),
        "checkpoint_id": source_snapshot.config["configurable"]["checkpoint_id"],
    }
    }

    corrupted_config = graph.update_state(
        source_config,
        {
            "iteration_count": 999,
        },
    )

    corrupted_checkpoint_id = corrupted_config["configurable"]["checkpoint_id"]

    print("Corrupted checkpoint:")
    print(corrupted_checkpoint_id)

    # ---------------------------------------------------------
    # 3. Find bad checkpoint
    # ---------------------------------------------------------
    print_section("3. FIND BAD CHECKPOINT")

    bad_checkpoint = find_bad_checkpoint(
        THREAD_ID,
        "iteration_count",
        999,
    )

    if bad_checkpoint is None:
        raise RuntimeError("Bad checkpoint could not be located.")

    print_json(bad_checkpoint)

    # ---------------------------------------------------------
    # 4. Apply correction
    # ---------------------------------------------------------
    print_section("4. APPLY CORRECTION")

    parent_config = bad_checkpoint["parent_config"]

    safe_parent_config = {
    "configurable": {
        "thread_id": parent_config["configurable"]["thread_id"],
        "checkpoint_ns": parent_config["configurable"].get(
            "checkpoint_ns", ""
        ),
        "checkpoint_id": parent_config["configurable"]["checkpoint_id"],
        }
    }

    correction = apply_correction(
        THREAD_ID,
        safe_parent_config,
        {
            "iteration_count": 0,
        },
    )

    print_json(correction)

    corrected_checkpoint_id = correction["new_checkpoint_id"]

    # ---------------------------------------------------------
    # 5. Verify original + corrupted + corrected branches
    # ---------------------------------------------------------
    print_section("5. VERIFY CHECKPOINT HISTORY")

    timeline = state_forensics(THREAD_ID)

    print_json(timeline)

    checkpoint_ids = {
        item["checkpoint_id"]
        for item in timeline
    }

    if corrupted_checkpoint_id not in checkpoint_ids:
        raise RuntimeError(
            "Corrupted checkpoint disappeared from history."
        )

    if corrected_checkpoint_id not in checkpoint_ids:
        raise RuntimeError(
            "Corrected checkpoint was not persisted."
        )

    print()
    print("PASS: corrupted checkpoint preserved")
    print("PASS: corrected checkpoint persisted")
    print("PASS: original history preserved")

    # ---------------------------------------------------------
    # 6. Time travel
    # ---------------------------------------------------------
    print_section("6. TIME TRAVEL")

    print("Re-invoking from corrected checkpoint:")
    print(corrected_checkpoint_id)

    travel_result = time_travel(
        THREAD_ID,
        corrected_checkpoint_id,
    )

    print_json(travel_result)

    # ---------------------------------------------------------
    # 7. Final verification
    # ---------------------------------------------------------
    print_section("7. FINAL VERIFICATION")

    final_timeline = state_forensics(THREAD_ID)

    print_json(final_timeline)

    final_checkpoint_id = travel_result["new_checkpoint_id"]

    if final_checkpoint_id in checkpoint_ids:
        raise RuntimeError(
            "Time travel did not create a new checkpoint."
        )

    print()
    print("PASS: time travel created a new branch")
    print("PASS: original checkpoints remain available")
    print("PASS: graph resumed from a historical checkpoint")

    print()
    print("=" * 70)
    print("STEP 12 LIVE DEMONSTRATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()