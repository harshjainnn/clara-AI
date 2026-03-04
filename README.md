## Clara AI – Zero-Cost Automation Pipeline

### Overview

Clara AI is a zero-cost automation pipeline that converts service business call recordings into structured AI agent configurations for Clara, an AI voice assistant used by service trade companies (e.g., electricians, plumbers, HVAC).

Given demo call recordings, the pipeline automatically generates:

- **Structured Account Memo JSON**
- **Retell-compatible Agent Draft Specification**
- **Versioned updates after onboarding**
- **A changelog describing modifications between versions**

All components are designed to be **fully automated**, **reproducible**, and **free to run** using only open-source or free-tier tools.

---

## Architecture

The end-to-end flow:

1. **Demo Call Recording**
2. **Whisper Speech-to-Text (local)**
3. **Transcript Processing**
4. **LLM Extraction (Google Gemini, free tier)**
5. **Account Memo JSON**
6. **Agent Spec Generator**
7. **Versioned Storage**
8. **Onboarding Update → v2 Agent + Changelog**

Automation is orchestrated with **n8n**, triggered via a webhook that calls a **Flask API** to run the pipeline.

---

## Key Technologies

- **Automation**: `n8n` (Docker, self-hosted)
- **Transcription**: `whisper` (local OpenAI Whisper)
- **LLM Extraction**: Google **Gemini** (free tier)
- **Storage**: Local JSON files
- **Backend API**: `Flask`
- **Versioning**: File-based version control (versioned folders + changelog JSON)

All tools are chosen to comply with a **zero-cost** constraint.

---

## Project Structure

```text
clara-automation-pipeline
│
├── dataset
│   └── demo_calls
│       ├── demo1.mp4
│       ├── demo2.mp4
│       ├── demo3.mp4
│       ├── demo4.mp4
│       └── demo5.mp4
│
├── outputs
│   └── accounts
│       └── <account_id>
│           ├── v1
│           │   ├── memo.json
│           │   └── agent_spec.json
│           ├── v2
│           │   ├── memo.json
│           │   └── agent_spec.json
│           └── changes.json
│
├── scripts
│   ├── api_server.py
│   ├── analyze_call.py
│   ├── generate_agent_spec.py
│   └── update_account.py
│
├── workflows
│   └── n8n_workflow.json
│
├── docker-compose.yml
└── README.md
```

- **`dataset/demo_calls/`**: Demo call recordings (`.mp4`) used as input.
- **`outputs/accounts/`**: Generated account data, specs, and changelogs.
- **`scripts/`**: Core Python scripts implementing the pipeline.
- **`workflows/`**: n8n workflow definition (`.json`).
- **`docker-compose.yml`**: Brings up n8n in Docker.

---

## Pipeline Components

### 1. Transcription (Whisper)

Call recordings are transcribed locally with OpenAI Whisper:

```bash
python -m whisper dataset/demo_calls/demo1.mp4 --model base
```

- Produces a transcript file for each demo call.
- These transcripts are consumed by downstream LLM extraction.

### 2. Account Memo Extraction (LLM / Gemini)

The transcript is processed with an LLM (Google Gemini) to extract structured account data into a memo JSON. Example:

```json
{
  "account_id": "account_123abc",
  "company_name": "Ben's Electric Solutions",
  "business_hours": {
    "days": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "start": "08:00",
    "end": "16:30",
    "timezone": ""
  },
  "services_supported": [],
  "office_address": "",
  "emergency_definition": [],
  "emergency_routing_rules": [],
  "non_emergency_routing_rules": [],
  "call_transfer_rules": {},
  "integration_constraints": [],
  "after_hours_flow_summary": "",
  "office_hours_flow_summary": "",
  "questions_or_unknowns": [],
  "notes": ""
}
```

- **Important**: Missing or uncertain information is left **blank or empty**, to avoid hallucination.

### 3. Agent Specification Generation

From the account memo, the system generates a **Retell-compatible agent configuration**:

```json
{
  "agent_name": "Ben's Electric Assistant",
  "voice_style": "professional friendly",
  "system_prompt": "...",
  "variables": {
    "business_hours": {},
    "office_address": ""
  },
  "call_transfer_protocol": {
    "attempts": 2,
    "fallback": "collect callback number"
  },
  "version": "v1"
}
```

- This specification can be adapted to Retell or other voice AI platforms.

### 4. Onboarding Update Pipeline

When onboarding information becomes available (simulated in this project), the pipeline:

- **Updates** the `memo.json`
- **Regenerates** the `agent_spec.json`
- **Creates a new version folder** (e.g., `v2`)
- **Writes a `changes.json`** describing differences between versions

Example layout:

```text
account_abc123
   ├── v1
   │   ├── memo.json
   │   └── agent_spec.json
   ├── v2
   │   ├── memo.json
   │   └── agent_spec.json
   └── changes.json
```

Example `changes.json`:

```json
{
  "version_from": "v1",
  "version_to": "v2",
  "changes": [
    "Added office_address",
    "Updated business_hours.timezone"
  ]
}
```

---

## Automation with n8n

The automation pipeline is controlled by **n8n** via a webhook.

### Workflow

1. **Webhook Trigger**
2. **HTTP Request**
3. **Flask API Server**
4. **Pipeline Execution**

The n8n webhook calls:

- **Endpoint**: `POST /process_call`  
- **Server**: Flask (`scripts/api_server.py`)

This endpoint runs the **entire processing pipeline** over the demo call recordings.

The n8n workflow is stored in:

- **`workflows/n8n_workflow.json`**

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url> clara-automation-pipeline
cd clara-automation-pipeline
```

### 2. Install Python Dependencies

Use Python 3.9+ (recommended).

```bash
pip install flask whisper requests
```

If needed, also ensure you have:

- `ffmpeg` installed (required by Whisper)
- API key/configuration for **Google Gemini** set via environment variables or config (implementation-specific in scripts).

### 3. Start n8n (Docker)

From the project root:

```bash
docker compose up
```

- n8n UI will be available at:  
  `http://localhost:5678`

Import or verify the workflow in `workflows/n8n_workflow.json` inside the n8n UI if needed.

### 4. Start the Flask API Server

Run:

```bash
python scripts/api_server.py
```

- Flask server will run at:  
  `http://localhost:5000`

---

## Running the Pipeline

With **n8n** and the **Flask API server** running:

### Trigger via Webhook (PowerShell Example)

```powershell
Invoke-RestMethod -Uri "http://localhost:5678/webhook-test/clara-call" -Method POST
```

- This triggers the n8n workflow.
- The workflow calls the Flask API (`/process_call`).
- The Flask API processes all available demo call recordings/transcripts.

---

## Outputs

Generated outputs are written to:

- **`outputs/accounts/`**

For each inferred `account_id`, you get:

- **`v1/memo.json`**: Initial extracted account memo
- **`v1/agent_spec.json`**: Initial agent specification
- **`v2/memo.json`**: Updated memo after onboarding
- **`v2/agent_spec.json`**: Updated agent spec
- **`changes.json`**: Human-readable changelog between versions

This structure makes it easy to:

- Inspect account configuration evolution
- Compare agent versions
- Integrate with further tooling or UI for diff viewing

---

## Known Limitations

- **Simplified prompt templates** for agent generation (can be expanded for production).
- **Onboarding updates are simulated**, not parsed from real onboarding calls.
- **Local JSON file storage** only (no database integration yet).
- No production-grade authentication, monitoring, or retries around the pipeline.

---

## Future Improvements

Potential next steps if moving towards production:

- **Direct Retell API integration** for creating and updating agents.
- **Supabase or similar DB** for persistent account storage and querying.
- **Automatic onboarding transcript parsing** to derive updates from real calls.
- **Diff viewer UI** for visualizing agent revisions between `v1`, `v2`, etc.
- **Dashboard / admin panel** to monitor accounts, runs, and errors.

---

## Zero-Cost Compliance

This project is intentionally built to incur **zero monetary cost**:

- **Whisper**: Local speech-to-text (no paid API calls).
- **Gemini**: Uses the **free API tier**.
- **n8n**: Self-hosted via Docker.
- **Storage**: Local JSON files, no paid database.
- **No paid subscriptions or proprietary APIs** are required.

---

## Demonstration

A Loom video (not included in this repository) demonstrates:

- Pipeline execution on a demo call
- Generated **account memo** and **agent configuration**
- Onboarding update producing **v2**
- Version comparison using the generated **changelog**

If you have access to the Loom link, you can follow along step-by-step with the repository.

---

## Author

- **Harsh Jain**

Contributions, issues, and suggestions are welcome via pull requests or issues on the repository.

