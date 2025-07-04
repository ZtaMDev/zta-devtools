from zta_devtools.utils import is_stdlib_module
import os
import re
import importlib.util
from zta_devtools.requirements import append_to_requirements, install_package_with_python, update_package_with_python, get_installed_version

IMPORT_RE = re.compile(r"^\s*(import|from)\s+([\w\.]+)")

def scan_project(directory="."):
    venv_python = detect_venv()

    if venv_python:
        use_venv = input("🧪 A virtual environment was detected in './venv'. Use it for installing/updating packages? (y/n): ").lower() == "y"
    else:
        use_venv = False

    python_exec = venv_python if use_venv else None

    found = scan_imported_modules(directory)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            match = IMPORT_RE.match(line)
                            if match:
                                module = match.group(2).split(".")[0]
                                found.add(module)
                except Exception:
                    continue

    if not found:
        print("⚠️ No imported modules found.")
        return

    print("\n🔍 Detected modules:")

    third_party_modules = []
    for mod in sorted(found):
        if is_stdlib_module(mod):
            print(f" ⏭️ {mod} (standard module)")
        else:
            third_party_modules.append(mod)

    if not third_party_modules:
        print("✅ No third-party modules detected.")
        return

    missing = []
    present = []

    for mod in sorted(third_party_modules):
        if is_installed(mod, python_exec):
            ver = get_installed_version(mod, python_exec)
            print(f" ✅ {mod} ({ver})")
            present.append(mod)
        else:
            print(f" ❌ {mod} (NOT INSTALLED)")
            missing.append(mod)

    # Save to requirements.txt
    if input("\n📄 Do you want to save all to requirements.txt? (y/n): ").lower() == "y":
        for mod in third_party_modules:
            append_to_requirements(mod, python_exec)

    # Install missing packages
    if missing and input("\n⬇️  Install missing packages? (y/n): ").lower() == "y":
        for mod in missing:
            install_package_with_python(mod, python_exec)

    # Update installed packages
    if present and input("\n⬆️  Update installed packages? (y/n): ").lower() == "y":
        for mod in present:
            update_package_with_python(mod, python_exec)

    # Clean unused dependencies
    clean_unused_requirements(set(third_party_modules), python_exec)


import os
import re

IMPORT_RE = re.compile(r"^\s*(from|import)\s+([a-zA-Z0-9_\.]+)")

def scan_imported_modules(directory="."):
    found = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            match = IMPORT_RE.match(line)
                            if match:
                                module = match.group(2).split(".")[0]
                                found.add(module)
                except Exception:
                    continue
    return found


def is_installed(module: str, python_exec=None) -> bool:
    if not python_exec:
        return importlib.util.find_spec(module) is not None
    else:
        import subprocess
        result = subprocess.run(
            [python_exec, "-c", f"import {module}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0


def detect_venv():
    if os.name == "nt":
        candidate = os.path.join("venv", "Scripts", "python.exe")
    else:
        candidate = os.path.join("venv", "bin", "python")
    return candidate if os.path.exists(candidate) else None


def clean_unused_requirements(used_modules: set, python_exec=None):
    if not os.path.exists("requirements.txt"):
        return

    with open("requirements.txt", "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    used = set(m.lower() for m in used_modules)
    keep = []
    unused = []

    for line in lines:
        if "==" in line:
            pkg = line.split("==")[0].strip().lower()
        else:
            pkg = line.strip().lower()

        if pkg in used:
            keep.append(line)
        else:
            unused.append(line)

    if not unused:
        print("✅ No unused dependencies in requirements.txt")
        return

    print("\n🧹 Unused dependencies detected:")
    for u in unused:
        print(f" ❌ {u}")

    if input("Do you want to remove them from requirements.txt? (y/n): ").lower() == "y":
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(keep) + "\n")
        print("🗑️ Cleanup complete.")
    else:
        print("ℹ️ requirements.txt not modified.")
