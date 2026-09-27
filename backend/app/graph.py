import os
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from .state import HRState
from .tools.hr_tools import (
    lookup_employee,
    search_hr_policy,
)

load_dotenv()


# ============================================================
# LLM - OpenRouter
# ============================================================

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not loaded. "
        "Check the .env file in the project root."
    )

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0,
    google_api_key=gemini_api_key,
)


# ============================================================
# Tools
# ============================================================

tools = [
    lookup_employee,
    search_hr_policy,
]

llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools)


# ============================================================
# Agent Node
# ============================================================

def agent_node(state: HRState) -> dict:
    """
    Ask the LLM to process the employee request.
    """

    messages = state.get("messages", [])

    system_message = SystemMessage(
        content=(
            "You are an HR onboarding assistant.\n\n"
            "Use the available tools when the employee's question "
            "requires employee data or HR policy information.\n\n"
            "Do not invent employee information or HR policy.\n\n"
            "If a tool can provide the required information, use the tool.\n"
            "If a tool has already provided information, use that information "
            "to answer the employee's question directly.\n"
            "If no tool is needed, answer the employee directly."
        )
    )

    # First agent call
    if not messages:
        human_message = HumanMessage(
            content=state["question"]
        )

        response = llm_with_tools.invoke(
            [
                system_message,
                human_message,
            ]
        )

        return {
            "messages": [
                human_message,
                response,
            ]
        }

    # Subsequent agent calls after a tool execution.
    # Do not add the SystemMessage again because Gemini
    # requires the function-call/tool-response turn order.
    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }

# ============================================================
# Tool Routing
# ============================================================

def should_continue(state: HRState) -> str:
    """
    Decide whether the graph should execute a tool or finish.
    """

    messages = state.get("messages", [])

    if not messages:
        return "end"

    last_message = messages[-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "end"


# ============================================================
# Step 1 - LLM Classification
# ============================================================

def classify_node(state: HRState) -> dict:
    """
    Classify the employee request into one HR category.
    """

    question = state["question"]

    prompt = f"""
You are an HR onboarding request classifier.

Classify the employee's request into exactly ONE of these categories:

PAPERWORK
ACCESS
BENEFITS
PAYROLL

Rules:

- PAPERWORK = onboarding documents, forms, certificates, paperwork
- ACCESS = HR portal, system access, login, account access
- BENEFITS = insurance, benefits enrollment, benefit questions
- PAYROLL = salary, payroll, payslip, first salary, payment questions

Return ONLY the category name.

Employee request:

{question}
"""

    result = llm.invoke(prompt)

    if isinstance(result.content, str):
        category = result.content.strip().upper()
    else:
        category = "".join(
            block.get("text", "")
            for block in result.content
            if isinstance(block, dict)
        ).strip().upper()

    valid_categories = {
        "PAPERWORK",
        "ACCESS",
        "BENEFITS",
        "PAYROLL",
    }

    if category not in valid_categories:
        raise ValueError(
            f"Invalid category returned by LLM: {category}"
        )

    return {
        "category": category
    }


# ============================================================
# Step 1 - Category Handlers
# ============================================================

def paperwork_handler(state: HRState) -> dict:
    return {
        "response": "Paperwork specialist handler received the request."
    }


def access_handler(state: HRState) -> dict:
    return {
        "response": "Access specialist handler received the request."
    }


def benefits_handler(state: HRState) -> dict:
    return {
        "response": "Benefits specialist handler received the request."
    }


def payroll_handler(state: HRState) -> dict:
    return {
        "response": "Payroll specialist handler received the request."
    }


# ============================================================
# Category Routing
# ============================================================

def route_category(state: HRState) -> str:
    return state["category"]


# ============================================================
# Build Step 1 Graph
# ============================================================

builder = StateGraph(HRState)

builder.add_node("classify", classify_node)

builder.add_node(
    "paperwork",
    paperwork_handler,
)

builder.add_node(
    "access",
    access_handler,
)

builder.add_node(
    "benefits",
    benefits_handler,
)

builder.add_node(
    "payroll",
    payroll_handler,
)


# START -> classify

builder.add_edge(
    START,
    "classify",
)


# classify -> category handler

builder.add_conditional_edges(
    "classify",
    route_category,
    {
        "PAPERWORK": "paperwork",
        "ACCESS": "access",
        "BENEFITS": "benefits",
        "PAYROLL": "payroll",
    },
)


# Category handlers -> END

builder.add_edge(
    "paperwork",
    END,
)

builder.add_edge(
    "access",
    END,
)

builder.add_edge(
    "benefits",
    END,
)

builder.add_edge(
    "payroll",
    END,
)


# Compile graph

graph = builder.compile()