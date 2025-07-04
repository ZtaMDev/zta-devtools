import platform
import sys
import shutil
import subprocess
import os

def show_info():
    print("📦 Current Python")
    print(f"  Version: {platform.python_version()}")
    print(f"  Executable: {sys.executable}")

    print("\n 🖥️  System")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Arch: {platform.machine()}")

    print("\n🔎 Other detected Python versions:")

    found = detect_all_pythons()
    current = os.path.abspath(sys.executable)

    for entry in found:
        mark = "✅" if os.path.abspath(entry["path"]) == current else "  "
        store = "🛒 Microsoft Store" if "WindowsApps" in entry["path"] else ""
        print(f"{mark} {entry['version']:8}  {entry['path']} {store}")


def detect_all_pythons():
    python_names = ["python", "python3", "python3.11", "python3.10", "python3.9", "py"]
    seen = set()
    results = []

    for name in python_names:
        path = shutil.which(name)
        if path and path not in seen:
            seen.add(path)
            version = get_python_version(path)
            if version:
                results.append({"path": path, "version": version})

    # Manually search in WindowsApps (Microsoft Store)
    if os.name == "nt":
        possible_dirs = [
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps"),
            r"C:\WindowsApps"
        ]
        for d in possible_dirs:
            if os.path.isdir(d):
                for exe in os.listdir(d):
                    if exe.startswith("python") and exe.endswith(".exe"):
                        full = os.path.join(d, exe)
                        if full not in seen:
                            version = get_python_version(full)
                            if version:
                                seen.add(full)
                                results.append({"path": full, "version": version})

    return results


def get_python_version(python_path):
    try:
        result = subprocess.run(
            [python_path, "-c", "import platform; print(platform.python_version())"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=1
        )
        return result.stdout.strip()
    except Exception:
        return None
