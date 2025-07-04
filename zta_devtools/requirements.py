# devtools_cli/requirements.py
import subprocess
import sys
from pathlib import Path
from rich.progress import Progress
from zta_devtools.utils import is_stdlib_module
from zta_devtools.utils import detect_venv  # function to detect venv
from zta_devtools.requirements import is_stdlib_module  # to filter standard modules
REQUIREMENTS_FILE = Path("requirements.txt")

def scan_vulnerabilities(requirements_file=REQUIREMENTS_FILE, python_exec=None):
    exec_path = python_exec or sys.executable

    if not Path(requirements_file).exists():
        print(f"⚠️ {requirements_file} not found.")
        if input("Do you want to generate requirements.txt with devtools_cli freeze? (y/n): ").lower() == "y":
            freeze_requirements()
        else:
            print("Aborting vulnerability scan.")
            return

    print(f"🔍 Scanning vulnerabilities in {requirements_file}...")

    try:
        result = subprocess.run(
            [exec_path, "-m", "safety", "check", "--file", str(requirements_file), "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )

        if result.returncode == 0:
            print("✅ No known vulnerabilities found.")
        else:
            import json
            vulns = json.loads(result.stdout)
            if not vulns:
                print("✅ No known vulnerabilities found.")
            else:
                print(f"⚠️ Found {len(vulns)} vulnerabilities:")
                for v in vulns:
                    print(f"- Package: {v['package_name']} {v['affected_versions']}")
                    print(f"  Severity: {v['severity']}")
                    print(f"  Vulnerability: {v['advisory']}")
                    print(f"  More info: {v['vulnerability_id']}\n")

    except Exception as e:
        print(f"❌ Error running Safety: {e}")

def get_installed_version(package_name: str, python_exec=None) -> str:
    try:
        args = [python_exec or sys.executable, "-m", "pip", "show", package_name]
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None


def append_to_requirements(package_name: str, python_exec=None):
    version = get_installed_version(package_name, python_exec)
    if is_stdlib_module(package_name):
        print(f"⏭️ {package_name} is a standard module, not added to requirements.txt")
        return
    if not version:
        print(f"⚠️ Could not get version of {package_name}")
        return

    line = f"{package_name}=={version}"
    updated = False

    if REQUIREMENTS_FILE.exists():
        with REQUIREMENTS_FILE.open("r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        new_lines = []
        for existing in lines:
            if existing.lower().startswith(package_name.lower() + "=="):
                new_lines.append(line)
                updated = True
            else:
                new_lines.append(existing)
        if not updated:
            new_lines.append(line)

        with REQUIREMENTS_FILE.open("w", encoding="utf-8") as f:
            f.write("\n".join(new_lines) + "\n")
    else:
        with REQUIREMENTS_FILE.open("w", encoding="utf-8") as f:
            f.write(line + "\n")

    if updated:
        print(f"♻️ Version of {package_name} updated in requirements.txt: {line}")
    else:
        print(f"📄 Added to requirements.txt: {line}")


from zta_devtools.utils import detect_venv

def install_package(package_name: str):
    venv = detect_venv()
    if venv:
        use_venv = input(f"\n🧪 Virtual environment detected in './venv'. Install {package_name} there? (y/n): ").lower() == "y"
    else:
        use_venv = False

    install_package_with_python(package_name, python_exec=venv if use_venv else None)


def update_package(package_name: str):
    venv = detect_venv()
    if venv:
        use_venv = input(f"\n🧪 Virtual environment detected in './venv'. Update {package_name} there? (y/n): ").lower() == "y"
    else:
        use_venv = False

    update_package_with_python(package_name, python_exec=venv if use_venv else None)



def install_package_with_python(package_name: str, python_exec=None):
    exec_path = python_exec or sys.executable
    print(f"📦 Installing {package_name}...")

    with Progress() as progress:
        task = progress.add_task("[cyan]Installing...", total=100)
        result = subprocess.run(
            [exec_path, "-m", "pip", "install", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        for _ in range(20):
            progress.update(task, advance=5)

    if result.returncode == 0:
        print(f"✅ {package_name} installed.")
        append_to_requirements(package_name, python_exec)
    else:
        print(f"❌ Error installing {package_name}.")


def update_package_with_python(package_name: str, python_exec=None):
    exec_path = python_exec or sys.executable
    print(f"⬆️  Updating {package_name}...")

    with Progress() as progress:
        task = progress.add_task("[magenta]Updating...", total=100)
        result = subprocess.run(
            [exec_path, "-m", "pip", "install", "--upgrade", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        for _ in range(20):
            progress.update(task, advance=5)

    if result.returncode == 0:
        print(f"✅ {package_name} updated.")
        append_to_requirements(package_name, python_exec)
    else:
        print(f"❌ Error updating {package_name}.")


def freeze_requirements():
    from zta_devtools.project_scan import scan_imported_modules
    venv_python = detect_venv()

    if venv_python:
        use_venv = input("🧪 Virtual environment detected in './venv'. Use it for freeze modules? (y/n): ").lower() == "y"
    else:
        use_venv = False

    python_exec = venv_python if use_venv else sys.executable

    print("🔍 Scanning modules used in the project...")
    used_modules = scan_imported_modules()
    filtered_modules = [m for m in used_modules if not is_stdlib_module(m)]

    if not filtered_modules:
        print("⚠️ No external modules detected to freeze.")
        return

    print(f"📄 Generating requirements.txt with used modules: {', '.join(filtered_modules)}")

    # Use pip freeze but filter only those modules
    result = subprocess.run(
        [python_exec, "-m", "pip", "freeze"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    freeze_lines = result.stdout.splitlines()

    # Filter freeze_lines to keep only used modules (by name)
    filtered_lines = []
    for line in freeze_lines:
        pkg_name = line.split("==")[0].lower()
        if pkg_name in [m.lower() for m in filtered_modules]:
            filtered_lines.append(line)

    if not filtered_lines:
        print("⚠️ No installed modules matching used ones were found.")
        return

    with REQUIREMENTS_FILE.open("w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines) + "\n")

    print("✅ requirements.txt generated with used modules.")

import re

def uninstall_package(package_name: str, python_exec=None):
    exec_path = python_exec or sys.executable
    print(f"🗑️ Uninstalling {package_name}...")

    with Progress() as progress:
        task = progress.add_task("[red]Uninstalling...", total=100)
        result = subprocess.run(
            [exec_path, "-m", "pip", "uninstall", "-y", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        for _ in range(20):
            progress.update(task, advance=5)

    if result.returncode == 0:
        print(f"✅ {package_name} uninstalled successfully.")
        remove_from_requirements(package_name)
    else:
        print(f"❌ Error uninstalling {package_name}.")


def remove_from_requirements(package_name: str):
    if not REQUIREMENTS_FILE.exists():
        return

    pattern = re.compile(rf"^{re.escape(package_name)}(==.+)?$", re.IGNORECASE)
    with REQUIREMENTS_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    with REQUIREMENTS_FILE.open("w", encoding="utf-8") as f:
        removed = False
        for line in lines:
            if pattern.match(line.strip()):
                removed = True
                continue
            f.write(line)

    if removed:
        print(f"🗒️ {package_name} removed from requirements.txt")
    else:
        print(f"ℹ️ {package_name} was not in requirements.txt")

from zta_devtools.project_scan import scan_imported_modules

def clean_unused_requirements(python_exec=None):
    """
    Cleans requirements.txt removing packages not imported in the project.
    """
    if not REQUIREMENTS_FILE.exists():
        print("⚠️ requirements.txt does not exist to clean.")
        return

    imported = scan_imported_modules()
    with REQUIREMENTS_FILE.open("r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    kept_lines = []
    removed_packages = []

    for line in lines:
        pkg = line.split("==")[0].lower()
        if pkg in imported or is_stdlib_module(pkg):
            kept_lines.append(line)
        else:
            removed_packages.append(pkg)

    with REQUIREMENTS_FILE.open("w", encoding="utf-8") as f:
        f.write("\n".join(kept_lines) + "\n")

    if removed_packages:
        print(f"🧹 Removed from requirements.txt: {', '.join(removed_packages)}")
    else:
        print("✅ No packages removed. All are used in the project.")


def show_outdated_packages(python_exec=None):
    exec_path = python_exec or sys.executable
    print("🔍 Checking for outdated packages...")

    result = subprocess.run(
        [exec_path, "-m", "pip", "list", "--outdated", "--format=columns"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    output = result.stdout.strip()
    if output:
        print(output)
    else:
        print("✅ All packages are up to date.")
