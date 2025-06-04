#!/usr/bin/env python3
import argparse
import sys
import os
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("command", help="Command to run. Available commands: help, create, start, install, pip, activate, venv, update", type=str,choices=["help","create","start","install","activate","venv","pip","update"],default="help",nargs="?")
    parser.add_argument("-v","--version", help="Show the version of PyPositron.", action="store_true")
    parser.add_argument("nargs",nargs=argparse.REMAINDER,help="Arguments for the command. Type 'positron <command> -h' for more information on the command.")
    args=parser.parse_args()
    argv=args.nargs
    
    # Check if help is requested for a specific command
    if args.command and ("-h" in argv or "--help" in argv):
        # Create sub-parsers with proper program names for help display
        if args.command == "install" or args.command == "pip":
            from py_positron import install
            install.install(argv)
            exit(0)
        elif args.command == "start":
            from py_positron import startproj as start
            start.start(argv)
            exit(0)
        elif args.command == "update":
            from py_positron import updatecmd as update
            update.update(argv)
            exit(0)
        elif args.command == "create":
            # Create a parser for create command help
            create_parser = argparse.ArgumentParser(prog=f"positron {args.command}")
            create_parser.add_argument("--directory", "-d", help="Directory to create the project in (default: current directory)", type=str, default=".")
            create_parser.add_argument("--name", "-n", help="Name of the project (default: demo_project)", type=str, default="demo_project")
            create_parser.add_argument("--author", "-a", help="Author name (optional)", type=str, default="")
            create_parser.add_argument("--description", help="Project description (optional)", type=str, default="")
            create_parser.add_argument("--no-venv", help="Do not create a virtual environment", action="store_true")
            create_parser.print_help()
            exit(0)
        elif args.command == "venv":
            # Create a parser for venv command help
            venv_parser = argparse.ArgumentParser(prog=f"positron {args.command}")
            venv_parser.add_argument("--root_path", "-r", help="Root path of the project (default: current directory)", type=str, default=".")
            venv_parser.print_help()
            exit(0)
        elif args.command == "build":
            # Create a parser for build command help
            build_parser = argparse.ArgumentParser(prog=f"positron {args.command}")
            build_parser.add_argument("--root_path", "-r", help="Root path of the project (default: current directory)", type=str, default=".")
            build_parser.add_argument("--output", "-o", help="Output filename for the executable", type=str)
            build_parser.add_argument("--build-type", help="Type of build to create", type=str, choices=["EXE", "EXE-ONEDIR", "DEB", "DMG", "APK"], default="EXE-ONEDIR")
            build_parser.add_argument("--onefile", help="Create a single executable file instead of a directory", action="store_true")
            build_parser.add_argument("--windows-console", help="Keep console window on Windows", action="store_true")
            build_parser.add_argument("--include-data", help="Include additional data files (format: source=destination)", action="append")
            build_parser.add_argument("--python-path", help="Specific Python interpreter to use for building", type=str)
            build_parser.print_help()
            exit(0)
        else:
            # For other commands, show basic help
            help_parser = argparse.ArgumentParser(prog=f"positron {args.command}")
            help_parser.add_argument("--help", "-h", help="Show this help message and exit", action="help")
            help_parser.print_help()
            exit(0)
    if args.version:
        import py_positron
        print("PyPositron version:", py_positron.__version__)
        exit(0)
    if args.command=="help":
        parser.print_help()
        exit(0)
    elif args.command=="create":
        from py_positron import create
        #import create
        create.create()
        exit(0)
    elif args.command=="install" or args.command=="pip":
        from py_positron import install
       # import install
        install.install(argv)
        exit(0)
    elif args.command=="start":
        from py_positron import startproj as start
        #import start
        start.start(argv)
    # elif args.command=="activate":
    #     #from py_positron import activate
    #     import activate
    #     activate.activate()
    #     exit(0)
    elif args.command=="venv":
        from py_positron import createvenv
        #import createvenv
        createvenv.venv()
        exit(0)
    elif args.command=="update":
        from py_positron import updatecmd as update
        #import update
        update.update(argv)
        exit(0)
    elif args.command=="build":
        from py_positron import buildcmd as build
        #import build
        build.build(argv)
        exit(0)
    else:
        print("NotImplemented")
        exit(0)
    
    