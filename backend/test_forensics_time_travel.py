from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


class TestState(TypedDict, total=False):
    value: str
    execution_count: int


def build_test_graph():
    checkpointer = MemorySaver()

    def process(state: TestState) -> dict[str, Any]:
        return {
            "value": f"{state.get('value', '')}-processed",
            "execution_count": state.get("execution_count", 0) + 1,
        }

    builder = StateGraph(TestState)
    builder.add_node("process", process)
    builder.add_edge(START, "process")
    builder.add_edge("process", END)

    return builder.compile(checkpointer=checkpointer)


def main():
    graph = build_test_graph()

    thread_id = "step12c-time-travel-test"

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # ---------------------------------------------------------
    # 1. Create the original execution.
    # ---------------------------------------------------------
    first_result = graph.invoke(
        {
            "value": "original",
            "execution_count": 0,
        },
        config=config,
    )

    history = list(graph.get_state_history(config))

    if len(history) < 2:
        raise AssertionError(
            "Expected at least two checkpoints in the original history."
        )

    # Select a historical checkpoint that contains state.
    historical_snapshot = None

    for snapshot in history:
        if snapshot.values and snapshot.values.get("value"):
            historical_snapshot = snapshot
            break

    if historical_snapshot is None:
        raise AssertionError("Could not find a historical checkpoint.")

    checkpoint_id = (
        historical_snapshot.config
        .get("configurable", {})
        .get("checkpoint_id", "")
    )

    if not checkpoint_id:
        raise AssertionError("Historical checkpoint has no checkpoint_id.")

    print("PASS: historical checkpoint selected")

    # ---------------------------------------------------------
    # 2. Time travel from the selected checkpoint.
    # ---------------------------------------------------------
    travel_config = {
        "configurable": {
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
        }
    }

    graph.invoke(
        None,
        config=travel_config,
    )

    # ---------------------------------------------------------
    # 3. Verify that history now contains additional checkpoints.
    # ---------------------------------------------------------
    new_history = list(graph.get_state_history(config))

    if len(new_history) <= len(history):
        raise AssertionError(
            "Time travel did not create a new checkpoint branch."
        )

    print("PASS: time travel created a new branch")

    # ---------------------------------------------------------
    # 4. Verify original checkpoint still exists.
    # ---------------------------------------------------------
    original_checkpoint_exists = any(
        snapshot.config
        .get("configurable", {})
        .get("checkpoint_id")
        == checkpoint_id
        for snapshot in new_history
    )

    if not original_checkpoint_exists:
        raise AssertionError(
            "Original checkpoint was destroyed."
        )

    print("PASS: original checkpoint still exists")

    # ---------------------------------------------------------
    # 5. Verify the original state remains in history.
    # ---------------------------------------------------------
    original_state_exists = any(
        snapshot.values.get("value") == historical_snapshot.values.get("value")
        for snapshot in new_history
    )

    if not original_state_exists:
        raise AssertionError(
            "Original state was not preserved."
        )

    print("PASS: original history was not destroyed")

    print()
    print("ALL STEP 12C TIME-TRAVEL TESTS PASSED")


if __name__ == "__main__":
    main()