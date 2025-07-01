import os
import sys
import json
import platform
import subprocess
from pathlib2 import Path
import argparse
import re
from packaging import version

def get_current_positron_version():
    """Get the version of the currently running PyPositron instance."""
    try:
        # Import the current PyPositron package to get its version
        import py_positron
        return py_positron.__version__
    except (ImportError, AttributeError):
        return None

def get_venv_positron_version(python_executable):
    """Get the PyPositron version installed in the specified Python environment."""
    try:
        # Run a command to get the version from the target environment
        cmd = [python_executable, "-c", "import py_positron; print(py_positron.__version__)"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return None

def compare_versions(current_version, venv_version):
    """Compare two version strings. Returns True if current > venv, False otherwise."""
    try:
        return version.parse(current_version) > version.parse(venv_version)
    except Exception:
        return False

def warn_version_mismatch(current_version, venv_version):
    """Display a warning about version mismatch."""
    print(f"\x1b[0;93;49m[WARN] Version mismatch detected!\x1b[0m")
    print(f"  Current PyPositron: v{current_version}")
    print(f"  Virtual environment PyPositron: v{venv_version}")
    print(f"  Your virtual environment has an older version of PyPositron.")
    print(f"  Run 'positron update' to update the virtual environment to the latest version.\x1b[0m")
    print()

def check_and_warn_version_mismatch(python_executable):
    """Check for version mismatch and warn the user if necessary."""
    current_version = get_current_positron_version()
    if not current_version:
        return  # Can't check if we don't know current version

    venv_version = get_venv_positron_version(python_executable)
    if not venv_version:
        return  # Can't check if we can't get venv version

    if compare_versions(current_version, venv_version):
        warn_version_mismatch(current_version, venv_version)

def check_and_warn_version_mismatch_linux(venv_path):
    """Check for version mismatch in Linux venv and warn the user if necessary."""
    current_version = get_current_positron_version()
    if not current_version:
        return  # Can't check if we don't know current version

    python_executable = os.path.join(venv_path, "bin", "python3")
    if os.path.exists(python_executable):
        venv_version = get_venv_positron_version(python_executable)
        if venv_version and compare_versions(current_version, venv_version):
            warn_version_mismatch(current_version, venv_version)

def start(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-venv", action="store_true", help="Run without venv, even if a compatible venv is present.")
    # Default to 'python' on Windows (to use PATH python.exe) and 'python3' elsewhere
    default_exe = "python" if platform.system().lower().startswith("win") else "python3"
    parser.add_argument(
        "--executable",
        default=default_exe,
        help=f"Python executable to use (default: {default_exe})"
    )
    args=parser.parse_args(argv)
    if not os.path.exists("config.json"):
        print("This folder does not contain a PyPositron project. Please navigate to the project root, where config.json is located.")
        print("You can create a new project with PyPositron create.")
        sys.exit(1)
    with open(os.path.abspath("config.json"), "r") as f:
        config = json.load(f)    # switch CWD to project root so all relative paths (entry_file, venvs) resolve correctly
    os.chdir(os.path.dirname(os.path.abspath("config.json")))
    if not os.path.exists(config["entry_file"]):
        print(f"The entry file {config['entry_file']} does not exist. Please create it or change the entry file path in config.json.")
        sys.exit(1)
    if not args.no_venv:
        if platform.system().lower().strip() == "windows":
            ps1_path = Path(__file__).parent / "python_executor.ps1"
            absolute = ps1_path.resolve()
            if config["has_venv"]:
                if os.path.exists(config.get("winvenv_executable","")) and config.get("winvenv_executable","") != "":
                    # Check for version mismatch before running
                    check_and_warn_version_mismatch(config["winvenv_executable"])
                    cmd = ["powershell","-NoProfile","-ExecutionPolicy", "Bypass","-Command", f"& '{absolute}' '{config['entry_file']}' '{os.getcwd()}' '{config['winvenv_executable']}'"]
                    result = subprocess.run(cmd,check=True)
                    if result.returncode != 0:
                        print("Error:", result.stderr, file=sys.stderr)
                        sys.exit(result.returncode)
                    sys.exit(0)
                else:
                    print("\x1b[0;93;49m[WARN]Running without venv, as this project does not contain a windows venv, but has a linux venv.\x1b[0m")
            # Use the executable from command line argument instead of config
            cmd = ["powershell","-NoProfile","-ExecutionPolicy", "Bypass","-Command", f"& '{absolute}' '{config['entry_file']}' '{os.getcwd()}' '{args.executable}'"]
            result = subprocess.run(cmd,check=True)
            if result.returncode != 0:
                print("Error:", result.stderr, file=sys.stderr)
                sys.exit(result.returncode)
            sys.exit(0)
        else:
            if config["has_venv"]:
                if os.path.exists(config.get("linuxvenv","")) and config.get("linuxvenv","") != "":
                    # Check for version mismatch before running
                    check_and_warn_version_mismatch_linux(config["linuxvenv"])
                    os.system("bash -c \'source \""+config["linuxvenv"]+"/bin/activate\" && "+args.executable+" \""+os.path.abspath(config["entry_file"])+"\"\'")
                    exit(0)
                else:
                    print("\x1b[0;93;49m[WARN]Running without venv, as this project does not contain a linux venv, but has a Windows venv.\x1b[0m")
            else:
                os.system(args.executable+" \""+os.path.abspath(config["entry_file"])+"\"")
                exit(0)
    else:
        if platform.system().lower().strip() == "windows":
            ps1_path = Path(__file__).parent / "python_executor.ps1"
            absolute = ps1_path.resolve()
            # Use the executable from command line argument instead of config
            cmd = ["powershell","-NoProfile","-ExecutionPolicy", "Bypass","-Command", f"& '{absolute}' '{config['entry_file']}' '{os.getcwd()}' '{args.executable}'"]
            result = subprocess.run(cmd,check=True)
            if result.returncode != 0:
                print("Error:", result.stderr, file=sys.stderr)
                sys.exit(result.returncode)
            else:
                os.system(args.executable+" \""+os.path.abspath(config["entry_file"])+"\"")
                exit(0)
