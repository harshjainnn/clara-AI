from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route("/process_call", methods=["POST"])
def process_call():

    print("\n--- Pipeline Started ---")

    # Step 1: Skip transcription and use existing transcript
    print("Using existing transcript (skipping Whisper)...")

    # Step 2: Extract structured account memo
    print("Running account memo extraction...")
    subprocess.run(
        "python scripts/analyze_call.py",
        shell=True
    )
    print("Account memo generated")

    # Step 3: Generate Retell agent draft spec
    print("Generating agent specification...")
    subprocess.run(
        "python scripts/generate_agent_spec.py",
        shell=True
    )
    print("Agent spec generated")

    # Step 4: Simulate onboarding update (creates v2 + changelog)
    print("Updating account to v2...")
    subprocess.run(
        "python scripts/update_account.py",
        shell=True
    )
    print("Account updated to v2")

    print("--- Pipeline Finished ---\n")

    return jsonify({"status": "pipeline completed"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)