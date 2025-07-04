import json
import subprocess
from pathlib import Path

SCRIPTS_FILE = Path("scripts.json")

def list_scripts():
    if not SCRIPTS_FILE.exists():
        print("⚠️ scripts.json not found in the project.")
        return

    with SCRIPTS_FILE.open("r", encoding="utf-8") as f:
        scripts = json.load(f)

    print("📜 Available scripts:")
    for name in scripts:
        print(f" - {name}")

def run_script(name):
    if not SCRIPTS_FILE.exists():
        print("⚠️ scripts.json not found in the project.")
        return

    with SCRIPTS_FILE.open("r", encoding="utf-8") as f:
        scripts = json.load(f)

    cmd = scripts.get(name)
    if not cmd:
        print(f"❌ Script '{name}' not found.")
        return

    print(f"🚀 Running '{name}': {cmd}")
    subprocess.run(cmd, shell=True)
