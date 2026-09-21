import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

from .state import HRState


load_dotenv()


# ---------------------------------------------------------
# LLM
# ---------------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)


# ---------------------------------------------------------
# Step 1: Classification Node
# ---------------------------------------------------------

def classify_node(state: HRState) -> dict:
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

    category = result.content.strip().upper()

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


# ---------------------------------------------------------
# Stub Handlers
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Conditional Routing
# ---------------------------------------------------------

def route_category(state: HRState) -> str:
    return state["category"]


# ---------------------------------------------------------
# Build Graph
# ---------------------------------------------------------

builder = StateGraph(HRState)


builder.add_node("classify", classify_node)

builder.add_node("paperwork", paperwork_handler)
builder.add_node("access", access_handler)
builder.add_node("benefits", benefits_handler)
builder.add_node("payroll", payroll_handler)


builder.add_edge(START, "classify")


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


builder.add_edge("paperwork", END)
builder.add_edge("access", END)
builder.add_edge("benefits", END)
builder.add_edge("payroll", END)


graph = builder.compile()