import json
import os
import subprocess
import sys
from pathlib import Path


def activate() -> None:
    """Activate PyPositron virtual environment."""
    config: dict[str, str] = load_config()

    # switch CWD to project root so all relative paths (entry_file, venvs) resolve correctly
    if Path(config["winvenv_executable"]).exists():
        windows_activation(config["winvenv_executable"])
    elif Path(config["linuxvenv"]).exists():
        linux_activation()
    else:
        exit_activation()


def windows_activation(env_path: str) -> None:
    """Activate the Windows virtual environment."""
    ps1_path: str = str(Path.cwd() / Path(env_path).parent / "activate.ps1")
    cmd: list[str] = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        f"& '{ps1_path}'",
    ]
    result = subprocess.run(cmd, check=True)
    if result.returncode != 0:
        print("Error:", result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    sys.exit(0)


def linux_activation() -> None:
    """Activate the Linux virtual environment."""
    cmd: str = 'bash -c "source linuxvenv/bin/activate"'
    os.system(cmd)


def exit_activation() -> None:
    """Exit the virtual environment setup."""
    print(
        "This project does not contain a PyPositron venv. "
        "Please create a new venv with PyPositron venv.",
    )
    sys.exit(1)


def load_config() -> dict[str, str]:
    """Load the configuration from config.json."""
    config_file: str = "config.json"
    if not Path(config_file).exists():
        print(
            "This folder does not contain a PyPositron project. "
            "Please navigate to the project root, where config.json is located."
            "\nYou can create a new project with PyPositron create.",
        )
        sys.exit(1)

    with Path.open(Path(config_file).resolve()) as f:
        return json.load(f)
