import glob
import subprocess

demo_calls = glob.glob("dataset/demo_calls/*.mp4")

for call in demo_calls:
    print("Processing:", call)
    subprocess.run("python scripts/analyze_call.py", shell=True)
    subprocess.run("python scripts/generate_agent_spec.py", shell=True)