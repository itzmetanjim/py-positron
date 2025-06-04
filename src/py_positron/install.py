import os
import sys
import argparse
import json
import platform
import subprocess
from pathlib2 import Path
def install(args):
    #pip installs a library
    parser=argparse.ArgumentParser()
    parser.add_argument("library", help="Library to install", type=str)
    parser.add_argument("--root_path","-r", help="Root path of the project", type=str,default="--",required=False,action="store")
    args=parser.parse_args(args)
    directory=args.root_path
    if args.root_path=="--":
        directory=os.getcwd()
    os.chdir(directory)
    if not os.path.exists(os.path.join(directory, "config.json")):
        print("It seems like the directory you are running this from is not a Positron project.")
        print("Please run this command from the root of your Positron project (where config.json is located).")
        print("To make a new positron project, run positron create.")
        exit(0)
    if not os.path.exists(os.path.join(directory,"winvenv", "Scripts")) and not os.path.exists(os.path.join(directory,"linuxvenv", "bin")):
        print("It seems like the project you are running this from does not have a venv..")
        print("To install a venv in Windows or Linux, run positron venv")
        exit(0)
    if platform.system().lower().strip() == "windows":
        if os.path.exists(os.path.join(directory,'winvenv', "Scripts")):    
            ps1_path = Path(__file__).parent / "winpackage_installer.ps1"
            absolute = ps1_path.resolve()
            cmd = ["powershell","-NoProfile","-ExecutionPolicy", "Bypass","-Command", f"& '{absolute}' {args.library} \'{directory}\'"]
            result = subprocess.run(cmd,check=True)
            if result.returncode != 0:
                print("Error:", result.stderr, file=sys.stderr)
                sys.exit(result.returncode)
        else:
            print("This project does not have a Windows venv, create one with positron venv")
            print("Note that you will have to install all extra libraries again in the Windows venv.")
            exit(0)
    elif platform.system().lower().strip() == "linux":
        if os.path.exists(os.path.join(directory,'linuxvenv', "bin")):
            os.system(f"bash -c \"source \'{os.path.join(directory,'linuxvenv', 'bin', 'activate')}\' && pip3 install {args.library}\"")
        elif os.path.exists(os.path.join(directory,'winvenv', "Scripts")):
            print("This project does not have a Linux venv, create one with positron venv")
            print("Note that you will have to install all extra libraries again in the Linux venv.")
            exit(0)
    elif platform.system().lower().strip() == "darwin":
        print("MacOS is not supported yet.")
        exit()
    