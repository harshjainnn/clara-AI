import json
import os

memo_base_path = "outputs/accounts"

if not os.path.exists(memo_base_path):
    print("No accounts found.")
    exit()

accounts = os.listdir(memo_base_path)

for account in accounts:

    v1_memo_path = os.path.join(memo_base_path, account, "v1", "memo.json")

    if not os.path.exists(v1_memo_path):
        continue

    print(f"\nGenerating agent spec for {account}")

    try:
        with open(v1_memo_path, "r") as f:
            memo = json.load(f)

        company_name = memo.get("company_name", "Service Company")

        agent_spec = {
            "agent_name": f"{company_name} Assistant",

            "voice_style": "professional friendly",

            "version": "v1",

            "system_prompt": f"""
You are Clara, an AI phone assistant for {company_name}.

Your job is to handle incoming customer calls professionally and efficiently.

BUSINESS HOURS FLOW:
- Greet the caller.
- Ask how you can help.
- Collect caller name and phone number.
- Determine the request.
- Transfer the call if required.
- If transfer fails, collect details and schedule callback.
- Confirm next steps.
- Ask if there is anything else.
- Close politely.

AFTER HOURS FLOW:
- Inform the caller that the office is currently closed.
- Ask if the issue is an emergency.
- If emergency:
    - Collect caller name
    - Collect phone number
    - Collect service address
    - Attempt emergency transfer
- If transfer fails:
    - Assure caller someone will follow up shortly.
- Ask if there is anything else.
- Close politely.

Important rules:
- Do not mention internal tools or function calls.
- Only collect information required for routing and dispatch.
""",

            "variables": {
                "company_name": company_name,
                "business_hours": memo.get("business_hours", {}),
                "office_address": memo.get("office_address", ""),
                "services_supported": memo.get("services_supported", [])
            },

            "call_transfer_protocol": {
                "max_attempts": 2,
                "timeout_seconds": 20,
                "fallback_action": "collect callback details and notify technician"
            },

            "fallback_protocol": {
                "action": "collect caller details",
                "fields": ["name", "phone_number", "reason_for_call"]
            }
        }

        output_path = os.path.join(memo_base_path, account, "v1", "agent_spec.json")

        with open(output_path, "w") as f:
            json.dump(agent_spec, f, indent=2)

        print(f"✅ Agent spec saved: {output_path}")

    except Exception as e:
        print(f"❌ Failed to generate agent spec for {account}")
        print(e)

print("\nAgent generation complete.")