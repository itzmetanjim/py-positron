import os
import sys
import json
import platform
import subprocess
from pathlib2 import Path
def venv():
    if not os.path.exists("config.json"):
        print("No config.json found. Please create a project first, or navigate to the project root directory.")
        sys.exit(1)
    with open(os.path.abspath("config.json"), "r") as f:
        config = json.load(f)
    if platform.system().lower().strip() == "windows":
        config["has_venv"] = True
        config["winvenv_executable"] = "winvenv/Scripts/python.exe"
        print("Creating venv and installing Positron (this may take a while)...")
        ps1_path = Path(__file__).parent / "winvenv_setup.ps1"
        absolute = ps1_path.resolve()
        cmd = ["powershell","-NoProfile","-ExecutionPolicy", "Bypass","-Command", f"& '{absolute}'"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("Error:", result.stderr, file=sys.stderr)
            print("Failed to create venv. Please create a venv manually and install Positron in it.")
            sys.exit(result.returncode)    
        print("Positron successfully installed in venv.")

    elif platform.system().lower().strip() == "linux":
        config["has_venv"] = True
        config["linuxvenv"] = os.path.join(os.getcwd(), "linuxvenv")
        print("Creating venv (this may take a while)...")
        os.system("python3 -m venv ./linuxvenv/")
        print("Activating venv...")
        os.system("bash -c \"source linuxvenv/bin/activate\"")
        print("Installing Positron in venv- if this fails, use pip to install it...")
        os.system('bash -c "source linuxvenv/bin/activate && pip3 install -U pip"')
        os.system('bash -c "source linuxvenv/bin/activate && pip3 install -U py_positron"')
        print("Positron installed in venv.")
    elif platform.system().lower().strip() == "darwin":
        print("Venv creation is not supported on MacOS through the project creation wizard.\nSee https://github.com/itzmetanjim/py-positron/wiki/Manually-creating-a-venv.") 
    else:
        print("""Could not create venv- Unsupported OS. Please create a venv manually and install Positron in it. See https://github.com/itzmetanjim/py-positron/wiki/Manually-creating-a-venv.""") 
        sys.exit(1)
    print("Updating config.json...")
    with open(os.path.abspath("config.json"), "w") as f:
        json.dump(config, f, indent=4)
    print("Venv created successfully.")
    print("You can now install libraries in the venv using positron install <library_name>.")