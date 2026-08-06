# 📁 Developer & GitHub Portfolio Guide
## Microsoft Agent Framework • Customer Support Handoff System

This document outlines the system documentation, API schemas, and deployment commands to help you present this multi-agent customer support project in your professional portfolio.

---

## 🏛 System Architecture & Workflow

The system is built on a **decentralized mesh topology** using the **conversational handoff pattern** from the Microsoft Agent Framework. Rather than a single massive chatbot doing all tasks, domain-specific specialist agents manage their respective tasks using exclusive tools, and hand back control when complete.

```
                  [👤 Customer Request]
                            │
                            ▼
                    [🤖 Triage Agent] 
                   (Entry Coordinator)
                    /       │       \
       handoff_to  /        │        \  handoff_to
        Billing   /         │         \  Technical
                 ▼          │          ▼
    [💳 Billing Agent]      │      [🔧 Technical Agent]
   (Refunds & Invoices)     │     (Logs & Password Resets)
         │                  │                  │
         └───────────┬──────┴──────┬───────────┘
                     │             │
          handoff_to │             │ handoff_to
            Triage   ▼             ▼   Triage
               [🤖 Triage]     [ℹ️ General Agent]
                              (Hours & Pricing Plans)
```

### Participant Agents:
1.  **Triage Agent (`Triage`)**: Receives all queries. Directs customer traffic to specialized agents and reviews ticket summaries.
2.  **Billing Specialist (`Billing`)**: Handles transactions. Integrates tools: `get_refund_status`, `process_virtual_refund`.
3.  **Technical Specialist (`Technical`)**: Performs diagnostics. Integrates tools: `check_server_status`, `send_password_reset_email`.
4.  **General Support Specialist (`General`)**: Handles basic pricing and hour info. Integrates tools: `get_pricing_info`.

---

## 💾 Session Checkpoint Persistence

For stateless REST environments, conversation continuity is maintained via **Agent Checkpoints**:
*   Checkpoints are isolated to individual customer directories: `history/checkpoints/{session_id}/` using `FileCheckpointStorage`.
*   During a conversation turn, the workflow state is stored as a file checkpoint. 
*   When a new message arrives, the API loads the checkpoint, delivers the user response mapping, and statelessly resumes execution.

---

## 🔌 REST API Documentation

The FastAPI backend exposes the following endpoints (available at `http://localhost:8000/api`):

| Endpoint | Method | Description | Payload/Response |
| :--- | :--- | :--- | :--- |
| `/api/chat` | `POST` | Sends a message to the active agent in the session workflow. | **Payload**: `{"message": "hi", "session_id": "cust_1"}`<br>**Response**: Array of generated text bubbles. |
| `/api/status` | `GET` | Returns aggregated metrics, sessions, active models, and provider status. | **Response**: JSON analytics including average response time and session time. |
| `/api/history` | `GET` | Retrieves full JSON message log for a session. | **Query Param**: `session_id=cust_1` |
| `/api/summary` | `GET` | Dynamically compiles a ticket details summary using AI (falls back to heuristics if slow). | **Query Param**: `session_id=cust_1` |
| `/api/resolve` | `POST` | Marks a session resolved and generates the final ticket summary. | **Payload**: `{"session_id": "cust_1"}` |
| `/api/handoff` | `POST` | Manually forces control of a session to a target agent (resets locks). | **Query Params**: `session_id=cust_1`, `target_agent=Technical` |
| `/api/settings` | `POST` | Configures the LLM provider and model name at runtime. | **Payload**: `{"provider": "ollama", "ollama_model": "llama3.2:3b"}` |
| `/api/export` | `GET` | Serves a downloadable Markdown transcript of the session. | **Query Param**: `session_id=cust_1` |

---

## 📦 Container Deployment

The application is fully containerized and can be launched using Docker Compose. It automatically establishes a bridge network to communicate with local Ollama instances on the host OS.

### Build and Run:
```bash
# Start uvicorn server in Docker (history/ and logs/ are mounted as volumes)
docker-compose up --build -d
```

### Verify Container Health:
```bash
# Query the API status from outside the container
curl -s http://localhost:8000/api/status
```

---

## 🧪 Integration Test Cases (Minimum 10)

The integration test suite ([`tests/test_scenarios.py`](file:///home/cherry/Desktop/1_Gen/Tasks/MAF/Customer%20support/tests/test_scenarios.py)) executes the following test scenarios to verify agent routing:

1.  **Refund Request**: "Hi, I want a refund for my order." → Billing Agent.
2.  **Payment Failed**: "My credit card payment failed yesterday, what should I do?" → Billing Agent.
3.  **Invoice Download**: "Where can I download my last month's invoice?" → Billing Agent.
4.  **Login Issue**: "I keep getting access denied when trying to login." → Technical Agent.
5.  **App Crash**: "The mobile app crashes every time I tap the home button." → Technical Agent.
6.  **Password Reset**: "I forgot my password, can you help me reset it?" → Technical Agent.
7.  **Business Hours**: "What are your office business hours?" → General Agent.
8.  **Pricing Inquiry**: "How much is the subscription fee for the Pro plan?" → General Agent.
9.  **Unknown/Clarification**: "I have a question about something." → Triage Agent (inquires further).
10. **Multi-topic routing (Billing → Technical)**: First checks refund (`Triage` → `Billing`), then requests password reset (`Billing` → `Triage` → `Technical`).
