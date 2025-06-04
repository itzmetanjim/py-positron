import os
import sys
import json
import platform
import subprocess
from pathlib2 import Path
# This script is used to activate the PyPositron virtual environment
def activate():
    if not os.path.exists("config.json"):
        print("This folder does not contain a PyPositron project. Please navigate to the project root, where config.json is located.")
        print("You can create a new project with PyPositron create.")
        sys.exit(1)
    with open(os.path.abspath("config.json"), "r") as f:
        config = json.load(f)
    # switch CWD to project root so all relative paths (entry_file, venvs) resolve correctly
    if platform.system().lower().strip() == "windows":
        if os.path.exists(config["winvenv_executable"]):
            os.chdir(os.path.dirname(os.path.abspath("config.json")))
            ps1_path = Path(os.path.join(os.getcwd(),os.path.dirname(config["winvenv_executable"]))) / "activate.ps1"
            absolute = ps1_path.resolve()
            cmd = ["powershell","-NoProfile","-ExecutionPolicy", "Bypass","-Command", f"& '{absolute}'"]
            result = subprocess.run(cmd,check=True)
            if result.returncode != 0:
                print("Error:", result.stderr, file=sys.stderr)
                sys.exit(result.returncode)
            sys.exit(0)
        else:
            print("This project does not contain a PyPositron Windows venv. Please create a new venv with PyPositron venv.")
            sys.exit(1)
    
    else:
        if os.path.exists(config["linuxvenv"]):
            os.system("bash -c \"source linuxvenv/bin/activate\"")
        else:
            print("This project does not contain a PyPositron Linux venv. Please create a new venv with PyPositron venv.")
            sys.exit(1)