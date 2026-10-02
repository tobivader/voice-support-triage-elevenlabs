# Voice Support Triage MVP — Build-Along Learning Guide

## Purpose

This guide is for me, not for Codex.

The objective is to finish a working MVP while understanding enough of the implementation to explain it confidently in an interview.

I should be able to answer:

1. What problem does this project solve?
2. Why is a voice agent useful here?
3. How does ElevenLabs communicate with my Python application?
4. What does each API endpoint do?
5. Why did I use GET for customer lookup and POST for escalation creation?
6. How does the agent decide whether to resolve or escalate?
7. How did I test that the system works?
8. What would I improve if this were a production system?

Do not optimize for writing the most code. Optimize for understanding the complete request flow.

---

# 1. Project in Plain English

The project simulates a common SaaS support workflow.

A customer says they cannot access a service.

Instead of a support analyst manually checking the account first, an ElevenLabs voice agent:

1. asks for the customer ID;
2. calls my Python API;
3. retrieves mock account information;
4. interprets the returned status;
5. explains the next step;
6. creates a structured escalation when engineering attention is appropriate.

The important part is not the fake account data.

The important part is demonstrating an integration pattern:

```text
customer conversation
→ AI agent
→ API call
→ application data
→ decision
→ action
→ clear customer communication
```

That pattern is transferable to real customer systems.

---

# 2. What I Am Demonstrating to ElevenLabs

This MVP should provide evidence for several Solutions Engineer skills.

## Customer-facing problem solving

The agent has to understand the customer's problem and communicate a useful next step.

## API integration

The ElevenLabs agent calls REST endpoints in a Python application.

## Python proficiency

The backend is implemented with Python and FastAPI.

## Solution architecture

I can explain how the voice interface, agent, API, data, and escalation workflow interact.

## Technical communication

The README and demo should make the solution understandable without needing to read the entire codebase.

## Scaling a repeated workflow

Account validation and initial escalation gathering are repeatable support tasks. The project turns them into a reusable workflow rather than treating every case as completely manual.

---

# 3. Learning Rule

Codex is my pair programmer.

It is not allowed to become the developer while I become the observer.

At the end of every phase I should be able to explain the code that was added.

If I cannot explain a section, I should ask Codex:

> Explain this code line by line at a junior software engineer level. Then ask me three short questions to check that I understand it before we continue.

I should not move forward because "the tests pass" if I do not understand why they pass.

---

# 4. Phase 0 — Environment and Repository

## What I should learn

- what a Python virtual environment does;
- why dependencies go in `requirements.txt`;
- what Git tracks;
- why `.gitignore` matters;
- why secrets should never be committed.

## Commands I should understand

Typical setup:

```bash
mkdir voice-support-triage-elevenlabs
cd voice-support-triage-elevenlabs
git init

python -m venv .venv
```

Activate the environment using the command appropriate for my OS.

Install dependencies after Codex creates the requirements file:

```bash
pip install -r requirements.txt
```

## Checkpoint

Before moving on, I should be able to explain:

> A virtual environment isolates this project's Python packages from the rest of my computer.

and:

> Git stores source-code history, while `.gitignore` prevents local/private files such as `.env` and the virtual environment from being committed.

---

# 5. Phase 1 — FastAPI and `/health`

## What I should learn

FastAPI is the HTTP server/application framework.

A route connects an HTTP method and URL to Python code.

Example mental model:

```text
Browser/request
GET /health
↓
FastAPI route function
↓
Python returns dictionary
↓
FastAPI serializes it to JSON
↓
Client receives response
```

## What `/health` proves

It does not prove the business logic works.

It proves that:

- the application started;
- HTTP requests reach it;
- it can return a response.

This becomes useful after deployment.

## Test manually

```bash
uvicorn app.main:app --reload
```

Then visit:

```text
http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok"}
```

## Checkpoint questions

I should be able to answer:

- What is FastAPI doing?
- What does GET mean?
- Why is `/health` useful?
- Where does the returned JSON come from?

---

# 6. Phase 2 — Customer Lookup

## Core concept: path parameter

For:

```text
GET /customers/CUST-102
```

`CUST-102` is a path parameter.

The route pattern is:

```text
/customers/{customer_id}
```

FastAPI takes the value from the URL and passes it to Python.

## Core concept: data lookup

My application reads the mock customer data and looks for the matching ID.

No database is needed because the goal is to demonstrate integration, not database administration.

## Core concept: 404

If the customer does not exist, the API should not return made-up data.

It should return HTTP 404.

That matters because a Solutions Engineer should think about failure cases, not only happy paths.

## Test manually

```bash
curl http://127.0.0.1:8000/customers/CUST-102
```

Then:

```bash
curl http://127.0.0.1:8000/customers/CUST-999
```

## Checkpoint

I should be able to explain why:

- one request returns 200;
- the other returns 404;
- the agent must not fabricate missing information.

---

# 7. Phase 3 — Escalation Endpoint

## Why POST?

GET retrieves information.

POST sends information to create something or trigger an action.

The escalation route receives troubleshooting context from the agent.

```text
POST /escalations
```

The request body includes:

- customer ID;
- issue;
- finding;
- troubleshooting already performed.

## Pydantic

Pydantic defines what valid input looks like.

Instead of accepting arbitrary JSON, the application specifies required fields and expected types.

That lets FastAPI reject malformed requests before my business logic runs.

## In-memory storage

For this MVP, escalations do not need a database.

They may exist only for the lifetime of the server process.

That is a conscious scope decision.

In production I might use:

- PostgreSQL;
- a ticketing platform;
- a CRM;
- an event queue.

But those are outside the MVP.

## Checkpoint

I should be able to explain:

- GET vs POST;
- what the request body is;
- what Pydantic validates;
- why persistence is intentionally omitted.

---

# 8. Phase 4 — Tests

## Why automated tests?

Manual testing proves that I tried a few requests.

Automated tests make expected behavior repeatable.

For example:

```text
Given CUST-102
When /customers/CUST-102 is requested
Then entitlement_enabled should be false
```

If a future code change breaks that behavior, the test should fail.

## What success means here

Tests should cover:

- health endpoint;
- known customer;
- missing entitlement;
- unknown customer;
- valid escalation;
- invalid escalation.

## Command

```bash
pytest
```

## Checkpoint

I should be able to explain at least one test using:

**Given → When → Then**

---

# 9. Phase 5 — Web Page

The frontend is intentionally small.

Its purpose is to give the recruiter somewhere to interact with the voice agent.

The page should make the demo obvious:

- what the project is;
- which sample IDs to try;
- what each ID demonstrates;
- where to start the voice conversation.

Do not spend the build session designing a fancy UI.

For a Solutions Engineer portfolio project, clarity beats visual complexity.

---

# 10. Phase 6 — Deployment

## Why deployment matters

Before deployment:

```text
ElevenLabs
X
cannot call http://127.0.0.1 on my laptop
```

After deployment:

```text
ElevenLabs
↓ HTTPS
Render public URL
↓
FastAPI application
```

A webhook tool needs an API it can reach.

## Render

The project uses a free Render web service.

Render builds the GitHub repository and runs the FastAPI server publicly.

## Important free-tier limitation

Free services can sleep when inactive.

That means the first demo request may take longer while the service wakes up.

This is acceptable for a portfolio MVP and should be mentioned in the README.

## Checkpoint

I should be able to answer:

- Why couldn't ElevenLabs simply call localhost?
- What does Render provide?
- What URL does ElevenLabs call after deployment?

---

# 11. Phase 7 — ElevenLabs Integration

This is the most important concept in the project.

## Agent

The ElevenLabs agent manages the conversation.

It should not have all customer data inside its prompt.

Instead it asks my API for the information it needs.

## Tool

A tool gives the agent permission and instructions to perform an external operation.

### `get_customer`

The agent calls:

```text
GET /customers/{customer_id}
```

It receives structured JSON.

### `create_escalation`

The agent calls:

```text
POST /escalations
```

It sends troubleshooting context.

## Webhook

A webhook tool is essentially:

> When this action is appropriate, make an HTTP request to this external URL.

The agent chooses when to call it based on:

- the tool description;
- parameter descriptions;
- the agent system prompt;
- the current conversation.

## Most important lesson

The LLM is not the source of truth for account status.

The API is.

The agent should use the API response to ground its answer.

That reduces hallucination and reflects a real integration pattern.

## Checkpoint

I should draw this without notes:

```text
voice
↓
ElevenLabs agent
↓ tool call
FastAPI endpoint
↓
JSON result
↓
ElevenLabs agent
↓
customer response
```

---

# 12. Phase 8 — End-to-End Validation

I need actual evidence that it works.

Do not invent a success percentage before testing.

Use a small results table in the README.

Example:

| Scenario | Expected | Actual | Pass? |
| --- | --- | --- | --- |
| CUST-101 | Healthy account; retry guidance | ... | ... |
| CUST-102 | Missing entitlement; escalation | ... | ... |
| CUST-103 | Inactive subscription; no engineering escalation | ... | ... |
| CUST-999 | Ask to verify ID; no fabricated data | ... | ... |

If one fails, that is useful information.

Fix it and document what changed.

## What I am evaluating

1. Did the agent call the correct tool?
2. Did it use the returned data correctly?
3. Did it avoid inventing data?
4. Did it escalate the right scenario?
5. Was the explanation understandable to a customer?

That is enough evaluation for this MVP.

---

# 13. Phase 9 — README and Documentation

The README is part of the project, not an afterthought.

A recruiter may spend more time on the README than the code.

The first screen should communicate:

**Voice Support Triage**

> A small ElevenLabs + FastAPI MVP that turns initial SaaS account troubleshooting into a reusable voice workflow.

Then quickly show:

- problem;
- solution;
- architecture;
- demo instructions;
- technology;
- results.

## Good documentation answers "why"

Weak:

> `main.py` contains the FastAPI app.

Better:

> The FastAPI backend acts as the integration layer between the ElevenLabs agent and mock SaaS account data. This keeps account state outside the model and lets the agent ground responses in retrieved data.

---

# 14. Phase 10 — GitHub

## Before pushing

Run:

```bash
git status
```

Look carefully for:

- `.env`;
- API keys;
- virtual environment;
- temporary files.

Run tests again:

```bash
pytest
```

Then commit and push.

## Repository quality check

Open the GitHub page in an incognito/private browser.

Ask:

> If I were an ElevenLabs recruiter and knew nothing about this project, could I understand the problem and test the demo in two minutes?

If not, improve the README.

---

# 15. What I Should Say About the Architecture in an Interview

A concise explanation:

> I wanted the voice model to handle the conversation but not become the source of truth for customer data. The ElevenLabs agent collects the customer ID and calls a FastAPI endpoint through a webhook tool. My API returns structured account data from a mock dataset. The agent then follows a small troubleshooting policy: it gives a next step for known account states and calls a second API endpoint to create a structured escalation when the account requires engineering attention. That separation let me keep the conversational layer, application logic, and data responsibilities clear.

I should understand every sentence before using it.

---

# 16. What I Should Say I Personally Built

After completing the project, I should be able to truthfully say:

- I defined the support use case.
- I designed the request flow.
- I built the Python/FastAPI endpoints.
- I created the mock data model.
- I configured the ElevenLabs webhook tools.
- I wrote the agent instructions.
- I embedded the voice agent.
- I wrote automated tests.
- I deployed the backend.
- I ran end-to-end scenarios.
- I documented the architecture and setup.

Codex assisted with implementation, but I should be able to explain and modify the code myself.

---

# 17. Common Problems and What They Teach Me

## API works locally but not in ElevenLabs

Likely causes:

- webhook still points at localhost;
- Render deployment failed;
- URL/path is wrong;
- service is waking up.

Lesson: external systems require publicly reachable endpoints.

## Agent does not call the tool

Likely causes:

- unclear tool description;
- unclear system prompt;
- parameter descriptions are weak;
- conversation does not provide required input.

Lesson: tool orchestration depends on interface design, not just code.

## Agent calls escalation too often

Likely cause:

- escalation rule is too vague.

Lesson: an AI workflow needs explicit decision boundaries.

## API returns validation error

Likely cause:

- request fields do not match the Pydantic model.

Lesson: integration contracts must match on both sides.

## Secret appears in Git

Stop.

Remove it from the repository and history as appropriate, rotate the secret, and review `.gitignore`.

Lesson: security hygiene is part of engineering.

---

# 18. Scope-Control Questions

Whenever I am tempted to add something, ask:

1. Does this help demonstrate customer-facing technical problem solving?
2. Does this prove Python/API/integration ability?
3. Will an ElevenLabs recruiter understand the added value immediately?
4. Can I explain it confidently?
5. Does it keep the project free?
6. Does it threaten completion?

If the answer is mostly no, do not add it.

---

# 19. Optional Improvements Only After the MVP Works

Do not build these until the core project is complete.

Possible later improvements:

- persist escalations to SQLite/PostgreSQL;
- integrate Jira or another ticketing system;
- use a real knowledge base;
- add post-call transcript processing;
- add authentication;
- add richer observability;
- add additional support scenarios;
- add a customer-facing status page;
- add evaluation automation.

These are future directions, not overnight requirements.

---

# 20. Final Self-Test

Before putting this project on an application, I should be able to answer without reading:

### Product

- What user problem does it solve?
- Why voice?
- What is deliberately out of scope?

### Python

- Where is the FastAPI app created?
- How are routes defined?
- How is customer data loaded?
- How is escalation input validated?

### HTTP

- Why GET for customer retrieval?
- Why POST for escalation?
- What do 200, 404, and 422 mean here?

### ElevenLabs

- What is the agent responsible for?
- What is a webhook tool?
- When does each tool run?
- Why isn't customer data stored in the prompt?

### Deployment

- Why is a public URL necessary?
- What does Render do?
- What limitation does the free service have?

### Testing

- What were my four end-to-end scenarios?
- Which ones passed?
- What bug did I encounter and how did I fix it?

### Solutions Engineering

- How could this pattern map to a real enterprise customer?
- Which parts are reusable?
- What would change for production?

If I can answer those comfortably, the project has achieved its real purpose.
