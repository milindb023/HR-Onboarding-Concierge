from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


class TestState(TypedDict, total=False):
    response: str
    status: str


def build_test_graph():
    def create_bad_state(state: TestState) -> dict[str, Any]:
        return {
            "response": "BAD_RESPONSE",
            "status": "BAD",
        }

    def finish(state: TestState) -> dict[str, Any]:
        return {}

    builder = StateGraph(TestState)

    builder.add_node("create_bad_state", create_bad_state)
    builder.add_node("finish", finish)

    builder.add_edge(START, "create_bad_state")
    builder.add_edge("create_bad_state", "finish")
    builder.add_edge("finish", END)

    return builder.compile(checkpointer=MemorySaver())


def find_bad_checkpoint(
    graph,
    thread_id: str,
    field: str,
    bad_value: Any,
):
    config = {"configurable": {"thread_id": thread_id}}

    for snapshot in graph.get_state_history(config):
        values = dict(snapshot.values or {})

        if values.get(field) == bad_value:
            return {
                "checkpoint_config": snapshot.config,
                "parent_config": snapshot.parent_config,
                "checkpoint_id": (
                    snapshot.config
                    .get("configurable", {})
                    .get("checkpoint_id", "")
                ),
                "parent_checkpoint_id": (
                    snapshot.parent_config
                    .get("configurable", {})
                    .get("checkpoint_id", "")
                    if snapshot.parent_config
                    else ""
                ),
            }

    return None


def test_find_and_correct_bad_checkpoint():
    graph = build_test_graph()

    thread_id = "step12b-test-thread"
    config = {"configurable": {"thread_id": thread_id}}

    graph.invoke(
        {"response": "", "status": "START"},
        config=config,
    )

    result = find_bad_checkpoint(
        graph,
        thread_id,
        "status",
        "BAD",
    )

    assert result is not None
    assert result["checkpoint_id"]
    assert result["parent_config"] is not None

    correction = graph.update_state(
        result["checkpoint_config"],
        {
            "status": "CORRECTED",
            "response": "Corrected response",
        },
    )

    assert correction["configurable"]["thread_id"] == thread_id
    assert correction["configurable"]["checkpoint_id"]

    corrected_state = graph.get_state(
        correction
    )

    assert corrected_state.values["status"] == "CORRECTED"
    assert corrected_state.values["response"] == "Corrected response"

    print("PASS: bad checkpoint located")
    print("PASS: parent checkpoint identified")
    print("PASS: correction applied with update_state()")
    print("PASS: corrected state persisted in checkpoint history")
    print()
    print("ALL STEP 12B TESTS PASSED")


if __name__ == "__main__":
    test_find_and_correct_bad_checkpoint()