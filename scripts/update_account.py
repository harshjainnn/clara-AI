import json
import os

accounts_dir = "outputs/accounts"

if not os.path.exists(accounts_dir):
    print("No accounts directory found")
    exit()

accounts = os.listdir(accounts_dir)

if not accounts:
    print("No accounts found")
    exit()

print("\nUpdating accounts...")

for account_id in accounts:

    print(f"\nUpdating account: {account_id}")

    v1_dir = os.path.join(accounts_dir, account_id, "v1")
    v2_dir = os.path.join(accounts_dir, account_id, "v2")

    memo_v1_path = os.path.join(v1_dir, "memo.json")

    if not os.path.exists(memo_v1_path):
        print("v1 memo not found, skipping...")
        continue

    # Load existing memo
    with open(memo_v1_path) as f:
        memo_v1 = json.load(f)

    # Copy memo to modify
    memo_v2 = json.loads(json.dumps(memo_v1))

    changes = []

    # --- Simulated onboarding updates ---
    if memo_v2.get("office_address", "") == "":
        memo_v2["office_address"] = "123 Main Street"
        changes.append("Added office_address")

    if memo_v2["business_hours"].get("timezone", "") == "":
        memo_v2["business_hours"]["timezone"] = "PST"
        changes.append("Updated business_hours.timezone")

    # ------------------------------------

    os.makedirs(v2_dir, exist_ok=True)

    # Save updated memo
    memo_v2_path = os.path.join(v2_dir, "memo.json")

    with open(memo_v2_path, "w") as f:
        json.dump(memo_v2, f, indent=2)

    print("✅ v2 memo created")

    # Regenerate agent spec using updated memo
    company_name = memo_v2.get("company_name", "Service Company")

    agent_spec_v2 = {
        "agent_name": f"{company_name} Assistant",
        "voice_style": "professional friendly",
        "version": "v2",

        "system_prompt": f"""
You are Clara, the AI phone assistant for {company_name}.

Business hours:
{memo_v2.get("business_hours")}

Services supported:
{memo_v2.get("services_supported")}

Office hours flow:
- greet caller
- ask how you can help
- collect name and phone number
- route or transfer call
- confirm next steps
- close politely

After hours flow:
- inform caller business is closed
- determine if emergency
- if emergency collect name, phone, address
- attempt transfer
- fallback if transfer fails
""",

        "variables": {
            "business_hours": memo_v2.get("business_hours"),
            "office_address": memo_v2.get("office_address"),
            "services_supported": memo_v2.get("services_supported")
        },

        "call_transfer_protocol": {
            "attempts": 2,
            "fallback": "collect callback number"
        },

        "fallback_protocol": "Collect name, phone number, reason for call."
    }

    agent_spec_path = os.path.join(v2_dir, "agent_spec.json")

    with open(agent_spec_path, "w") as f:
        json.dump(agent_spec_v2, f, indent=2)

    print("✅ v2 agent spec generated")

    # Create changelog
    changelog = {
        "account_id": account_id,
        "version_from": "v1",
        "version_to": "v2",
        "changes": changes
    }

    changelog_path = os.path.join(accounts_dir, account_id, "changes.json")

    with open(changelog_path, "w") as f:
        json.dump(changelog, f, indent=2)

    print("✅ changelog created")

print("\n--- All Accounts Updated Successfully ---")