# HR Onboarding Concierge

AI-powered HR onboarding assistant built as a Phase 3 AI Engineering Masters Program project.

The application uses LangGraph to triage employee onboarding questions across paperwork, system access, benefits, and payroll. It combines LLM classification, tool calling, specialist subgraphs, supervisor routing, parallel specialist execution, persistence, guardrails, gated writes, human approval, and checkpoint forensics/time travel.

## Project Goals

The system is designed to:

- Classify HR onboarding requests.
- Route requests to the appropriate specialist workflow.
- Retrieve employee and HR policy information through tools.
- Maintain persistent conversation/checkpoint state.
- Protect against prompt injection and PII-related risks.
- Summarize long conversations.
- Execute specialist workflows in parallel.
- Prepare and gate system-account provisioning requests.
- Require human approval before executing protected writes.
- Support approve, deny, and edit-and-approve workflows.
- Inspect checkpoint history and identify anomalous state.
- Correct a bad checkpoint and re-run the graph from a historical checkpoint without destroying the original history.

## Technology Stack

- Python 3.13.15
- LangGraph
- LangChain Core
- Google Gemini
- FastAPI
- SQLite checkpoint persistence
- Pydantic
- python-dotenv
- HTTPX
- Uvicorn

## Project Structure

```text
HR-Onboarding-Concierge/
|
|-- backend/
|   |
|   |-- app/
|   |   |-- graph.py
|   |   |-- state.py
|   |   |-- main.py
|   |   |-- persistence.py
|   |   |-- guardrails.py
|   |   |-- summarization.py
|   |   |-- specialists.py
|   |   |-- supervisor.py
|   |   |-- parallel.py
|   |   |-- synthesizer.py
|   |   |-- severity.py
|   |   |-- severity_node.py
|   |   |-- write_access.py
|   |   |-- write_policy.py
|   |   |-- write_request.py
|   |   |-- write_request_node.py
|   |   |-- write_draft_node.py
|   |   |-- provisioning.py
|   |   |-- approval.py
|   |   |-- approval_node.py
|   |   |-- approval_interrupt.py
|   |   |-- approval_execute.py
|   |   |-- approval_complete.py
|   |   |-- approval_routing.py
|   |   `-- forensics.py
|   |
|   |-- demo_step12.py
|   |-- test_*.py
|   `-- checkpoints.sqlite  (generated at runtime)
|
|-- .env.example
|-- .gitignore
|-- requirements.txt
`-- README.md