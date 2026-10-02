import os

from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from .approval_interrupt import approval_interrupt_node
from .approval_node import approval_request_node
from .approval_routing import route_approval
from .approval_execute import execute_approved_write

from .approval_complete import approval_complete_node

from .state import HRState
from .tools.hr_tools import (
    lookup_employee,
    search_hr_policy,
)
from .persistence import checkpointer
from .summarization import (
    MAX_MESSAGES_BEFORE_SUMMARY,
    prepare_summary_context,
    build_summary_text,
)
from .guardrails import evaluate_input
from .specialists import (
    paperwork_graph,
    access_graph,
    benefits_graph,
    payroll_graph,
)

from .supervisor import supervisor_node
from .parallel import build_parallel_sends
from .synthesizer import synthesizer_node

from .severity_node import severity_node
from .write_draft_node import write_draft_node
from .write_request_node import write_request_node

MAX_ITERATIONS = 5
MAX_DUPLICATE_TOOL_CALLS = 2

load_dotenv()


# ============================================================
# LLM - Gemini
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

def summarize_conversation(
    messages,
    existing_summary: str = "",
) -> str:
    """
    Create a compact summary of older conversation messages.

    This function uses the LLM only when context summarization
    is actually required.
    """

    old_messages, _ = prepare_summary_context(messages)

    if not old_messages:
        return existing_summary

    conversation_text = build_summary_text(old_messages)

    if existing_summary:
        prompt = f"""
You are maintaining a concise memory for an HR onboarding assistant.

Existing conversation summary:
{existing_summary}

Additional older conversation:
{conversation_text}

Create an updated concise summary.

Preserve:
- Employee identifiers
- Employee-related facts
- Questions already asked
- Important HR policy information
- Actions already taken
- Unresolved issues
- Important tool results

Do not invent information.

Return only the summary.
"""
    else:
        prompt = f"""
You are maintaining a concise memory for an HR onboarding assistant.

Summarize the following older conversation:

{conversation_text}

Preserve:
- Employee identifiers
- Employee-related facts
- Questions already asked
- Important HR policy information
- Actions already taken
- Unresolved issues
- Important tool results

Do not invent information.

Return only the summary.
"""

    result = llm.invoke(prompt)

    if isinstance(result.content, str):
        return result.content.strip()

    return "".join(
        block.get("text", "")
        for block in result.content
        if isinstance(block, dict)
    ).strip()

# ============================================================
# Input Guardrail
# ============================================================

def guardrail_node(state: HRState) -> dict:
    """
    Validate the user's request before it reaches the LLM agent.

    Blocked requests never enter the agent/tool loop.
    """

    result = evaluate_input(state["question"])

    if not result.allowed:
        return {
            "guardrail_blocked": True,
            "guardrail_reason": result.reason,
            "escalated": True,
            "response": (
                "I cannot process this request because it contains "
                "information or instructions that cannot be handled "
                "by the HR onboarding assistant."
            ),
        }

    return {
        "guardrail_blocked": False,
        "guardrail_reason": result.reason,
    }


def route_guardrail(state: HRState) -> str:
    """
    Route blocked requests away from the agent/tool workflow.
    """

    if state.get("guardrail_blocked", False):
        return "blocked"

    return "allowed"
# ============================================================
# Agent Node
# ============================================================

def agent_node(state: HRState) -> dict:
    """
    Ask the LLM to process the employee request and record tool calls.

    Context summarization is performed only when the conversation
    exceeds the configured message threshold.
    """

    messages = state.get("messages", [])
    iteration_count = state.get("iteration_count", 0)
    tool_call_history = state.get("tool_call_history", [])
    conversation_summary = state.get("conversation_summary", "")

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

    # --------------------------------------------------------
    # First agent call
    # --------------------------------------------------------

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
            ],
            "iteration_count": iteration_count + 1,
            "tool_call_history": tool_call_history + [
                f"{tool_call.get('name', '')}:{tool_call.get('args', {})}"
                for tool_call in getattr(response, "tool_calls", [])
            ],
        }

    # --------------------------------------------------------
    # Existing conversation
    # --------------------------------------------------------

    # Only summarize when this is a new user turn.
    #
    # A tool-loop message has tool_calls. We must not summarize
    # in the middle of that loop because Gemini requires the
    # function-call/tool-response message ordering.
    last_message = messages[-1]

    is_tool_loop_message = bool(
        getattr(last_message, "tool_calls", [])
    )

    should_summarize_now = (
        len(messages) > MAX_MESSAGES_BEFORE_SUMMARY
        and not is_tool_loop_message
    )

    if should_summarize_now:
        old_messages, recent_messages = prepare_summary_context(
            messages
        )

        if old_messages:
            new_summary = summarize_conversation(
                old_messages,
                conversation_summary,
            )

            summary_message = SystemMessage(
                content=(
                    "Conversation memory from earlier messages:\n\n"
                    f"{new_summary}"
                )
            )

            response = llm_with_tools.invoke(
                [
                    system_message,
                    summary_message,
                    *recent_messages,
                ]
            )

            new_tool_call_history = list(tool_call_history)

            for tool_call in getattr(response, "tool_calls", []):
                tool_name = tool_call.get("name", "")
                tool_args = tool_call.get("args", {})

                fingerprint = f"{tool_name}:{tool_args}"

                new_tool_call_history.append(fingerprint)

            return {
                "messages": [response],
                "conversation_summary": new_summary,
                "iteration_count": iteration_count + 1,
                "tool_call_history": new_tool_call_history,
            }

    # --------------------------------------------------------
    # Normal existing-message flow
    # --------------------------------------------------------

    response = llm_with_tools.invoke(messages)

    new_tool_call_history = list(tool_call_history)

    for tool_call in getattr(response, "tool_calls", []):
        tool_name = tool_call.get("name", "")
        tool_args = tool_call.get("args", {})

        fingerprint = f"{tool_name}:{tool_args}"

        new_tool_call_history.append(fingerprint)

    return {
        "messages": [response],
        "iteration_count": iteration_count + 1,
        "tool_call_history": new_tool_call_history,
    }

# ============================================================
# Tool Routing
# ============================================================

def should_continue(state: HRState) -> str:
    """
    Decide whether the graph should execute another tool call,
    finish, or escalate.
    """

    iteration_count = state.get("iteration_count", 0)

    # Safety limit
    if iteration_count >= MAX_ITERATIONS:
        return "escalate"

    messages = state.get("messages", [])

    if not messages:
        return "end"

    last_message = messages[-1]

    tool_calls = getattr(last_message, "tool_calls", [])

    if not tool_calls:
        return "end"

    # Check duplicate tool calls
    history = state.get("tool_call_history", [])

    for tool_call in tool_calls:
        tool_name = tool_call.get("name", "")
        tool_args = tool_call.get("args", {})

        fingerprint = f"{tool_name}:{tool_args}"

        duplicate_count = history.count(fingerprint)

        if duplicate_count >= MAX_DUPLICATE_TOOL_CALLS:
            return "escalate"

    return "tools"


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




# ============================================================
# Escalation Node
# ============================================================

def escalation_node(state: HRState) -> dict:
    return {
        "escalated": True,
        "response": (
            "The request requires human review because "
            "the agent reached a safety limit."
        ),
    }


# ============================================================
# Build Main Agent Graph
# ============================================================

builder = StateGraph(HRState)


# Agent node

builder.add_node("guardrail", guardrail_node)
builder.add_node("classify", classify_node)

builder.add_node("supervisor", supervisor_node)
builder.add_node("parallel_dispatch", lambda state: {})
builder.add_node("synthesizer", synthesizer_node)
builder.add_node("write_request", write_request_node)
builder.add_node("severity", severity_node)
builder.add_node("write_draft", write_draft_node)
builder.add_node("approval_request", approval_request_node)
builder.add_node("approval_interrupt", approval_interrupt_node)
builder.add_node("approval_execute", execute_approved_write)
builder.add_node("approval_complete", approval_complete_node)


builder.add_node("paperwork_specialist", paperwork_graph)
builder.add_node("access_specialist", access_graph)
builder.add_node("benefits_specialist", benefits_graph)
builder.add_node("payroll_specialist", payroll_graph)

builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)
builder.add_node("escalate", escalation_node)

builder.add_edge(START, "guardrail")

builder.add_conditional_edges(
    "guardrail",
    route_guardrail,
    {
        "allowed": "classify",
        "blocked": "escalate",
    },
)

builder.add_edge(
    "classify",
    "supervisor",
)

def route_supervisor(state: HRState) -> str:
    return state["supervisor_route"]

builder.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "PAPERWORK": "parallel_dispatch",
        "ACCESS": "parallel_dispatch",
        "BENEFITS": "parallel_dispatch",
        "PAYROLL": "parallel_dispatch",
        "FINISH": END,
    },
)

builder.add_conditional_edges(
    "parallel_dispatch",
    build_parallel_sends,
)

builder.add_edge("paperwork_specialist", "synthesizer")
builder.add_edge("access_specialist", "synthesizer")
builder.add_edge("benefits_specialist", "synthesizer")
builder.add_edge("payroll_specialist", "synthesizer")

builder.add_edge("synthesizer", "write_request")
builder.add_edge("write_request", "severity")
builder.add_edge("severity", "write_draft")
builder.add_edge("write_draft", "approval_request")
builder.add_edge("approval_request", "approval_interrupt")
builder.add_conditional_edges(
    "approval_interrupt",
    route_approval,
    {
        "approved": "approval_execute",
        "denied": "approval_complete",
        "pending": "approval_interrupt",
        "not_required": "agent",
    },
)

builder.add_edge("approval_execute", "approval_complete")
builder.add_edge("approval_complete", END)

# agent -> tools / end / escalate
builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": "supervisor",
        "escalate": "escalate",
    },
)


# tools -> agent
builder.add_edge(
    "tools",
    "agent",
)


# escalate -> END
builder.add_edge(
    "escalate",
    END,
)


# ============================================================
# Compile Graph With SQLite Persistence
# ============================================================

graph = builder.compile(
    checkpointer=checkpointer
)


# ============================================================
# Persistent Ticket Entry Point
# ============================================================

def run_ticket(question: str, thread_id: str) -> dict:
    """
    Run an HR onboarding request using a persistent thread.

    A new thread starts with the question field.
    An existing thread receives the new question as a HumanMessage
    so the conversation can continue from the saved checkpoint.
    """

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    existing_state = graph.get_state(config)

    if existing_state.values.get("messages"):
        return graph.invoke(
            {
                "question": question,
                "messages": [
                    HumanMessage(content=question)
                ],
            },
            config,
        )

    return graph.invoke(
        {
            "question": question,
        },
        config,
    )


# ============================================================
# Persistent Streaming Entry Point
# ============================================================

def stream_ticket(question: str, thread_id: str):
    """
    Stream an HR onboarding request using a persistent thread.
    """

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    existing_state = graph.get_state(config)

    if existing_state.values.get("messages"):
        input_state = {
            "question": question,
            "messages": [
                HumanMessage(content=question)
            ],
        }
    else:
        input_state = {
            "question": question,
        }

    return graph.stream(
        input_state,
        config,
        stream_mode="values",
    )
