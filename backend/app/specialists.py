from langgraph.graph import END, START, StateGraph

from .state import HRState


# ============================================================
# PAPERWORK SPECIALIST
# ============================================================

def paperwork_specialist_node(state: HRState) -> dict:
    question = state["paperwork_question"]

    finding = (
        "Paperwork specialist reviewed the request: "
        f"{question}"
    )

    return {
        "specialist_findings": [finding],
    }


paperwork_builder = StateGraph(HRState)

paperwork_builder.add_node(
    "paperwork_specialist",
    paperwork_specialist_node,
)

paperwork_builder.add_edge(
    START,
    "paperwork_specialist",
)

paperwork_builder.add_edge(
    "paperwork_specialist",
    END,
)

paperwork_graph = paperwork_builder.compile()


# ============================================================
# ACCESS SPECIALIST
# ============================================================

def access_specialist_node(state: HRState) -> dict:
    question = state["access_question"]

    finding = (
        "Access specialist reviewed the request: "
        f"{question}"
    )

    return {
        "specialist_findings": [finding],
    }


access_builder = StateGraph(HRState)

access_builder.add_node(
    "access_specialist",
    access_specialist_node,
)

access_builder.add_edge(
    START,
    "access_specialist",
)

access_builder.add_edge(
    "access_specialist",
    END,
)

access_graph = access_builder.compile()


# ============================================================
# BENEFITS SPECIALIST
# ============================================================

def benefits_specialist_node(state: HRState) -> dict:
    question = state["benefits_question"]

    finding = (
        "Benefits specialist reviewed the request: "
        f"{question}"
    )

    return {
        "specialist_findings": [finding],
    }


benefits_builder = StateGraph(HRState)

benefits_builder.add_node(
    "benefits_specialist",
    benefits_specialist_node,
)

benefits_builder.add_edge(
    START,
    "benefits_specialist",
)

benefits_builder.add_edge(
    "benefits_specialist",
    END,
)

benefits_graph = benefits_builder.compile()


# ============================================================
# PAYROLL SPECIALIST
# ============================================================

def payroll_specialist_node(state: HRState) -> dict:
    question = state["payroll_question"]

    finding = (
        "Payroll specialist reviewed the request: "
        f"{question}"
    )

    return {
        "specialist_findings": [finding],
    }


payroll_builder = StateGraph(HRState)

payroll_builder.add_node(
    "payroll_specialist",
    payroll_specialist_node,
)

payroll_builder.add_edge(
    START,
    "payroll_specialist",
)

payroll_builder.add_edge(
    "payroll_specialist",
    END,
)

payroll_graph = payroll_builder.compile()