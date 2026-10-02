from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from backend.app.state import HRState
from backend.app.forensics import _get_anomaly_flags


def build_test_graph():
    builder = StateGraph(HRState)

    def normal_node(state: HRState):
        return {
            "response": "Onboarding request processed successfully."
        }

    def suspicious_node(state: HRState):
        return {}

    builder.add_node("normal", normal_node)
    builder.add_node("suspicious", suspicious_node)

    builder.add_edge(START, "normal")
    builder.add_edge("normal", END)

    builder.add_edge(
        "suspicious",
        END,
    )

    return builder.compile(
        checkpointer=MemorySaver()
    )


def test_empty_response_anomaly():
    flags = _get_anomaly_flags(
        {
            "response": "",
        },
        (),
    )

    assert "EMPTY_RESPONSE" in flags

    print("PASS: EMPTY_RESPONSE anomaly detected")


def test_guardrail_anomaly_flag():
    flags = _get_anomaly_flags(
        {
            "guardrail_blocked": True,
        },
        ("agent",),
    )

    assert "GUARDRAIL_BLOCKED" in flags

    print("PASS: GUARDRAIL_BLOCKED anomaly detected")


def test_approval_pending_flag():
    flags = _get_anomaly_flags(
        {
            "approval_status": "PENDING",
        },
        ("approval_interrupt",),
    )

    assert "APPROVAL_PENDING" in flags

    print("PASS: APPROVAL_PENDING anomaly detected")


def test_loop_proximity_flag():
    flags = _get_anomaly_flags(
        {
            "iteration_count": 2,
        },
        ("agent",),
    )

    assert "LOOP_PROXIMITY" in flags

    print("PASS: LOOP_PROXIMITY anomaly detected")


def test_forensics_history():
    graph = build_test_graph()

    config = {
        "configurable": {
            "thread_id": "forensics-test-thread",
        }
    }

    graph.invoke(
        {
            "question": "Test onboarding question",
        },
        config=config,
    )

    history = list(
        graph.get_state_history(config)
    )

    assert len(history) >= 2

    print(
        "PASS: checkpoint history contains "
        f"{len(history)} snapshots"
    )

    for snapshot in history:
        assert snapshot.config["configurable"].get(
            "checkpoint_id"
        )

    print("PASS: checkpoints contain checkpoint IDs")


if __name__ == "__main__":
    print("STEP 12A - CHECKPOINT FORENSICS")
    print("--------------------------------")

    test_empty_response_anomaly()
    test_guardrail_anomaly_flag()
    test_approval_pending_flag()
    test_loop_proximity_flag()
    test_forensics_history()

    print()
    print("ALL STEP 12A FORENSICS TESTS PASSED")