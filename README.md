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

## Run the application

The project uses Python 3.13.15. From the project root, activate the virtual environment and start the FastAPI server:

```powershell
.\.venv\Scripts\activate
uvicorn backend.app.main:app --reload
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) for the minimal browser interface.

## API endpoints

- `GET /` serves the browser UI.
- `POST /run` runs an onboarding request for a thread.
- `POST /stream` streams graph state updates as server-sent events.
- `GET /pending-approvals` lists pending approval requests.
- `POST /approve` approves a pending request.
- `POST /deny` denies a pending request.
- `POST /edit-and-approve` submits edited employee and system values for approval.
- `POST /forensics` returns a thread's checkpoint timeline.
- `POST /forensics/find-bad-checkpoint` locates a checkpoint containing a specified value.
- `POST /forensics/apply-correction` applies a correction to a checkpoint.
- `POST /forensics/time-travel` resumes execution from a selected checkpoint.
