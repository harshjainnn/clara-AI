import json
import requests
import os
import uuid
import glob

# Gemini API key
API_KEY = "AIzaSyDo_CJIbFvIuVOen6A1_cWPBlC6MSbSnqs"

# Gemini API endpoint
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

headers = {"Content-Type": "application/json"}

# Ensure output folders exist
os.makedirs("outputs/accounts", exist_ok=True)

# Task tracker file
tracker_path = "outputs/task_tracker.json"

# Load existing tasks if present
if os.path.exists(tracker_path):
    with open(tracker_path, "r") as f:
        tasks = json.load(f)
else:
    tasks = []

# Get all transcripts
transcripts = glob.glob("dataset/demo_calls/*.txt")

for transcript_file in transcripts:

    print(f"\nProcessing transcript: {transcript_file}")

    with open(transcript_file, "r", encoding="utf-8") as f:
        transcript = f.read()

    account_id = f"account_{uuid.uuid4().hex[:6]}"

    prompt = f"""
You are an AI system extracting structured account setup data for Clara,
an AI phone assistant for service businesses.

From the transcript below, extract information and return ONLY valid JSON
with this exact schema:

{{
  "account_id": "{account_id}",
  "company_name": "",
  "business_hours": {{
    "days": [],
    "start": "",
    "end": "",
    "timezone": ""
  }},
  "office_address": "",
  "services_supported": [],
  "emergency_definition": [],
  "emergency_routing_rules": [],
  "non_emergency_routing_rules": [],
  "call_transfer_rules": {{
    "attempts": "",
    "fallback_action": ""
  }},
  "integration_constraints": [],
  "after_hours_flow_summary": "",
  "office_hours_flow_summary": "",
  "questions_or_unknowns": [],
  "notes": ""
}}

Rules:
- Do NOT hallucinate missing information
- Leave unknown values empty
- Return ONLY JSON

Transcript:
{transcript}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]

        text = text.replace("```json", "").replace("```", "").strip()

        memo = json.loads(text)

        account_id = memo["account_id"]

        output_dir = f"outputs/accounts/{account_id}/v1"
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, "memo.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(memo, f, indent=2)

        print(f"✅ Memo saved: {output_path}")

        # Create task tracker entry
        task = {
            "account_id": account_id,
            "company": memo.get("company_name", ""),
            "status": "Demo call processed"
        }

        tasks.append(task)

    except Exception as e:
        print("❌ Error parsing Gemini response")
        print(e)
        print(json.dumps(data, indent=2))

# Save task tracker
with open(tracker_path, "w") as f:
    json.dump(tasks, f, indent=2)

print("\n📌 Task tracker updated.")