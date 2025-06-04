#!usr/bin/env python3
import os
import sys
import json
import platform
import datetime
import subprocess
from pathlib2 import Path
import argparse
import py_positron
def create():
    license_template="""
    Copyright {text}

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    """
    checkmarkpng_path = os.path.join(os.path.dirname(__file__), "example/checkmark.png")
    mainpy=""
    indexhtml=""
    with open(os.path.join(os.path.dirname(__file__), "example/main_app.py"), "r") as f:
        mainpy=f.read()
    with open(os.path.join(os.path.dirname(__file__), "example/index.html"), "r") as f:
        indexhtml=f.read()
    print("Welcome to the PyPositron project creation wizard!\nPress ^C to exit.")
    try:
        directory = input("\033[1;92;49mProject directory (leave empty to use current directory):\033[0m ")
        if directory =="":
            print("Using current directory.")
            directory = os.getcwd()
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            print(f"\033[1;91;49m[ERROR] Invalid directory syntax: {e}\033[0m")
            exit(1)
        print("You can change any of the following options later in \033[4;39;49mconfig.json\033[0m.")
        projname=input("\033[1;92;49mProject name (default: demo_project):\033[0m ")
        if projname == "":
            projname = "demo_project"
        authorname=input("\033[1;92;49mAuthor name (optional):\033[0m ")
        description=input("\033[1;92;49mProject description (optional):\033[0m ")
        project_version=input("\033[1;92;49mProject version (default: 0.1.0):\033[0m ")
        if project_version == "":
            project_version = "0.1.0"
        print("A virtual environment (venv) can be used to isolate the project enviroment from the main python installation.")
        print("This can be useful to avoid conflicts between different projects and packages.")
        print("The venv will be automatically activated and deactivated by PyPositron.")
        print("It is recommended to use a venv for most projects, but you will need to install all your packages seperately on the venv.")
        print("If you are using Mac, you have to create a venv manually https://github.com/itzmetanjim/py-PyPositron/wiki/Manually-creating-a-venv") 
        print("You can create a venv in your project later by using \033[4;39;49mpositron venv\033[0m.")
        venv_choice=input("\033[1;92;49mCreate a venv inside the project directory? y/N: \033[0m ")
        while venv_choice.lower() not in ["y", "n", "yes", "no",""]:
                print("\033[1;91;49m[ERROR] Invalid input. Please enter y or n.\033[0m")
                venv_choice=input("\033[1;92;49mCreate a venv inside the project directory? y/N: \033[0m ")
        venv=False
        if venv_choice.lower() in ["y", "yes"]:
            venv = True
        elif venv_choice.lower() in ["n", "no", ""]:
            venv = False
        if venv:
            print("You can install libraries in a PyPositron project venv by using positron pip install <library>.")
            print("The PyPositron package will be automatically installed in the venv when the project is created.")
            print("If it fails, create a venv using positron venv.")
        print("\033[1;92;49mSelected options (can be changed):\033[0m")
        print("\033[1;92;49mDirectory:\033[0m ", directory)
        print("\033[1;92;49mProject name:\033[0m  ", projname)
        print("\033[1;92;49mAuthor name:\033[0m  ", authorname)
        print("\033[1;92;49mDescription:\033[0m  ", description)
        print("\033[1;92;49mA venv will be created.\033[0m " if venv else "\033[1;92;49mNo venv will be created, but you can create one later.\033[0m ")
        print("You can change these options and more through \033[4;39;49mconfig.json\033[0m.")
        input("\033[1;92;49mPress Enter to continue or ^C to exit and change the options\033[0m")
        print("Creating project...")
        config={
            "name": projname,
            "author": authorname,
            "description": description,
            "has_venv": venv,
            "requirements":"requirements.txt",
            "entry_file":"backend/main.py",
            "positron_version":py_positron.__version__, #Placeholder, replace with positron.__version__
            "python_version":f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}",
            "project_version": project_version,
            "winvenv_executable": "winvenv/Scripts/python.exe" if venv and platform.system().lower().strip()=="windows" else "",
            "linuxvenv":"",
            "license_type": "MIT",
            "license_file": "LICENSE",     
        }
    except KeyboardInterrupt:
        exit(0)
    except EOFError:
        exit(0)
    if platform.system().lower().strip() == "linux":
        config.update({"linuxvenv": "linuxvenv" if venv else ""})
    print("Creating config.json...")
    with open(os.path.join(os.path.abspath(directory), "config.json"), "w") as f:
        json.dump(config, f, indent=4)
    print("Creating license file...")
    with open(os.path.join(os.path.abspath(directory), "LICENSE"), "w") as f:
        f.write(license_template.format(text=str(datetime.datetime.now().year)+" "+authorname))
    print("Creating directories and example files...")
    print("Creating backend...")
    try:
        os.mkdir(os.path.join(os.path.abspath(directory), "backend"))
    except FileExistsError:
        pass
    print("Creating frontend...")
    try:
        os.mkdir(os.path.join(os.path.abspath(directory), "frontend"))
    except FileExistsError:
        pass
    print("Creating example files...")
    with open(os.path.join(os.path.abspath(directory), "backend/main.py"), "w") as f:
        f.write(mainpy)
    with open(os.path.join(os.path.abspath(directory), "frontend/index.html"), "w") as f:
        f.write(indexhtml)
    with open(os.path.join(os.path.abspath(directory), "frontend/checkmark.png"), "wb") as f:
        with open(checkmarkpng_path, "rb") as f2:
            f.write(f2.read())
    print("Changing to the project directory...")
    os.chdir(os.path.abspath(directory))
    if venv:
        if platform.system().lower().strip() == "windows":
            print("Creating venv and installing PyPositron (this may take a while)...")
            ps1_path = Path(__file__).parent / "winvenv_setup.ps1"
            absolute = ps1_path.resolve()
            cmd = ["powershell","-NoProfile","-ExecutionPolicy", "Bypass","-Command", f"& '{absolute}'"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print("Error:", result.stderr, file=sys.stderr)
                print("Failed to create venv. Please create a venv manually and install PyPositron in it.")
                sys.exit(result.returncode)    
            print("PyPositron successfully installed in venv.")

        elif platform.system().lower().strip() == "linux":
            print("Creating venv (this may take a while)...")
            os.system("python3 -m venv ./linuxvenv/")
            print("Activating venv...")
            os.system("bash -c \"source linuxvenv/bin/activate\"")
            print("Installing PyPositron in venv- if this fails, use pip to install it...")
            os.system('bash -c "source linuxvenv/bin/activate && pip3 install -U pip"')
            os.system('bash -c "source linuxvenv/bin/activate && pip3 install -U py_positron"') 
            print("PyPositron installed in venv.")
        elif platform.system().lower().strip() == "darwin":
            print("Venv creation is not supported on MacOS through the project creation wizard.\nSee https://github.com/itzmetanjim/py-positron/wiki/Manually-creating-a-venv.") 
        else:
            print("""Could not create venv- Unsupported OS. Please create a venv manually and install PyPositron in it. See https://github.com/itzmetanjim/py-positron/wiki/Manually-creating-a-venv.""") 
    print("\033[1;92;49mProject created successfully!\033[0m")
    print("\033[1;92;49mYou can now run your project with:\033[0m")
    print("\033[4;39;49mpositron start\033[0m")
