import argparse
from zta_devtools import info, venv_utils, requirements, project_scan, watcher
from zta_devtools import scripts
from zta_devtools.docs_generator import scan_directory_for_docs, generate_markdown_docs
from zta_devtools.utils import is_stdlib_module, detect_venv
import subprocess
import os
import sys
import urllib.request
import tempfile
import platform

def main():
    parser = argparse.ArgumentParser(
        prog="devtools",
        description="Useful tools for developers"
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("info", help="Show Python environment and system info")

    parser_git = subparsers.add_parser("install-git", help="(requires admin rights) Automatically install Git if not installed")

    subparsers.add_parser("docs", help="Generate automatic documentation in DOCUMENTATION.md")

    subparsers.add_parser("vuln-scan", help="Scan vulnerabilities using Safety on requirements.txt")

    init_venv_parser = subparsers.add_parser("init-venv", help="Create a virtual environment in ./venv and optionally install modules")
    init_venv_parser.add_argument(
        "modules",
        nargs="*",
        help="Optional modules to install after creating the virtual environment"
    )

    delete_venv_parser = subparsers.add_parser("delete-venv", help="Delete the virtual environment ./venv")
    delete_venv_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Delete without confirmation"
    )

    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a package and remove it from requirements.txt")
    uninstall_parser.add_argument("package", help="Name of the package to uninstall")

    clean_parser = subparsers.add_parser("clean", help="Clean requirements.txt by removing unused packages")
    subparsers.add_parser("list-scripts", help="List scripts defined in scripts.json")

    outdated_parser = subparsers.add_parser("outdated", help="Show installed packages with available updates")

    run_script_parser = subparsers.add_parser("run-script", help="Run a defined script")
    run_script_parser.add_argument("name", help="Name of the script to run")

    install_parser = subparsers.add_parser("install", help="Install a package and save it to requirements.txt")
    install_parser.add_argument("package")

    update_parser = subparsers.add_parser("update", help="Update a package")
    update_parser.add_argument("package")

    subparsers.add_parser("scan", help="Scan modules used in the project")
    subparsers.add_parser("freeze", help="Generate the current requirements.txt file")
    subparsers.add_parser("watch", help="Watch for changes in .py files")

    args = parser.parse_args()

    if args.command == "info":
        info.show_info()
    elif args.command == "install-git":
        install_git()
    elif args.command == "docs":
        docs = scan_directory_for_docs("devtools_cli")
        generate_markdown_docs(docs)
    elif args.command == "vuln-scan":
        requirements.scan_vulnerabilities()
    elif args.command == "init-venv":
        venv_utils.create_venv_and_install(install_modules=args.modules)
    elif args.command == "install":
        requirements.install_package(args.package)
    elif args.command == "update":
        requirements.update_package(args.package)
    elif args.command == "scan":
        project_scan.scan_project()
    elif args.command == "freeze":
        requirements.freeze_requirements()
    elif args.command == "watch":
        watcher.start_watch()
    elif args.command == "delete-venv":
        venv_utils.delete_venv(force=args.force)
    elif args.command == "uninstall":
        requirements.uninstall_package(args.package)
    elif args.command == "clean":
        requirements.clean_unused_requirements()
    elif args.command == "list-scripts":
        scripts.list_scripts()
    elif args.command == "run-script":
        scripts.run_script(args.name)
    elif args.command == "outdated":
        requirements.show_outdated_packages()
    else:
        parser.print_help()


def is_git_installed():
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_git_windows():
    print("Downloading Git installer for Windows...")
    url = "https://github.com/git-for-windows/git/releases/latest/download/Git-64-bit.exe"
    tmp_path = os.path.join(tempfile.gettempdir(), "Git-64-bit.exe")
    urllib.request.urlretrieve(url, tmp_path)
    print("Installer downloaded, starting silent installation...")

    install_cmd = [tmp_path, "/VERYSILENT", "/NORESTART"]
    try:
        subprocess.run(install_cmd, check=True)
        print("Git installed successfully.")
    except subprocess.CalledProcessError:
        print("Error installing Git.")


def install_git_linux():
    print("Installing Git using apt...")
    try:
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "git"], check=True)
        print("Git installed successfully.")
    except subprocess.CalledProcessError:
        print("Error installing Git. Please run manually: sudo apt install git")


def install_git():
    if is_git_installed():
        print("Git is already installed.")
        return

    os_system = platform.system()
    if os_system == "Windows":
        install_git_windows()
    elif os_system == "Linux":
        install_git_linux()
    elif os_system == "Darwin":
        print("Please install Git manually on macOS, for example using Homebrew: brew install git")
    else:
        print(f"Operating system {os_system} is not supported for automatic Git installation.")
