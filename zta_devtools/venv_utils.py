import os
import subprocess
import sys
from rich.progress import Progress
import time

def create_venv_and_install(install_modules=None):
    if os.path.exists("venv"):
        print("⚠️ Virtual environment 'venv' already exists.")
    else:
        print("Creating virtual environment 'venv'...")

        with Progress() as progress:
            task = progress.add_task("[green]Creating virtual environment...", total=100)
            proc = subprocess.Popen([sys.executable, "-m", "venv", "venv"])
            while proc.poll() is None:
                progress.update(task, advance=10)
                time.sleep(0.1)
            progress.update(task, completed=100)

        if proc.returncode != 0:
            print("❌ Error creating the virtual environment.")
            return

        print("✅ Virtual environment created.")

    # Define python path inside the venv
    venv_python = "venv\\Scripts\\python.exe" if os.name == "nt" else "venv/bin/python"

    if install_modules:
        print(f"\n📦 Installing modules inside the virtual environment: {', '.join(install_modules)}")

        with Progress() as progress:
            task = progress.add_task("[cyan]Installing packages...", total=100)
            proc = subprocess.Popen(
                [venv_python, "-m", "pip", "install"] + install_modules,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            while proc.poll() is None:
                progress.update(task, advance=10)
                time.sleep(0.1)
            progress.update(task, completed=100)

        if proc.returncode == 0:
            print("✅ Modules installed successfully.")
        else:
            print("❌ Error installing modules inside the virtual environment.")

    print("\nTo activate the virtual environment, use:")
    if os.name == "nt":
        print("venv\\Scripts\\activate")
    else:
        print("source venv/bin/activate")

import shutil
import os

def delete_venv(force=False):
    venv_path = "venv"
    if not os.path.exists(venv_path):
        print("⚠️ Virtual environment 'venv' does not exist to delete.")
        return

    if not force:
        confirm = input("⚠️ Are you sure you want to delete the virtual environment 'venv'? This cannot be undone. (y/n): ").lower()
        if confirm != "y":
            print("❌ Deletion cancelled.")
            return

    try:
        shutil.rmtree(venv_path)
        print("✅ Virtual environment 'venv' deleted successfully.")
    except Exception as e:
        print(f"❌ Error deleting 'venv': {e}")

import os
import sys

def detect_venv():
    venv_path = os.path.join(os.getcwd(), "venv")
    if not os.path.isdir(venv_path):
        return None

    if os.name == "nt":  # Windows
        python_exec = os.path.join(venv_path, "Scripts", "python.exe")
    else:  # Unix/Linux/Mac
        python_exec = os.path.join(venv_path, "bin", "python")

    if os.path.isfile(python_exec):
        return python_exec
    return None
