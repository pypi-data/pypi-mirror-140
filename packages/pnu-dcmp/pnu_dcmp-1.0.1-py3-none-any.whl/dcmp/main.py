#!/usr/bin/env python
""" dcmp - compare two directories, deduplicating if needed
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

import getopt
import hashlib
import logging
import os
import re
import signal
import sys

# Version string used by the what(1) and ident(1) commands:
ID = "@(#) $Id: dcmp - compare two directories, deduplicating if needed v1.0.1 (February 25, 2022) by Hubert Tournier $"

BLOCK = 1048576

IDENTICAL = "="
DIFFERENT = "!"
MISSING_IN_DIR2 = "+"
MISSING_IN_DIR1 = "-"

OK = 0
SAME = 0
DIFFERENCES = 1
ERROR = 2

# Default parameters. Can be overcome by environment variables, then command line options
parameters = {
    "Follow symlinks": True,
    "Verbose mode": False,
    "Silent mode": False,
    "Dedup mode": False,
}


################################################################################
def _initialize_debugging(program_name):
    """Debugging set up"""
    console_log_format = program_name + ": %(levelname)s: %(message)s"
    logging.basicConfig(format=console_log_format, level=logging.DEBUG)
    logging.disable(logging.INFO)


################################################################################
def _display_help():
    """Displays usage and help"""
    print("usage: dcmp [--debug] [--help|-?] [--version]", file=sys.stderr)
    print("       [-h|--nosymlinks] [-s|--silent|--quiet]", file=sys.stderr)
    print("       [-v|--verbose] [--dedup]", file=sys.stderr)
    print("       [--] directory1 directory2", file=sys.stderr)
    print(
        "  -------------------  ---------------------------------------------------------",
        file=sys.stderr
    )
    print("  --dedup              In dir1, remove empty dirs and files", file=sys.stderr)
    print("                       which are identical to those in dir2", file=sys.stderr)
    print("  -h|--nosymlinks      Do not follow symlinks", file=sys.stderr)
    print(
        "  -s|--silent|--quiet  Print nothing for differing dirs; return exit status only",
        file=sys.stderr
    )
    print("  -v|--verbose         Print identical dirs and files names", file=sys.stderr)
    print("  --debug              Enable debug mode", file=sys.stderr)
    print("  --help|-?            Print usage and this help message and exit", file=sys.stderr)
    print("  --version            Print version and exit", file=sys.stderr)
    print("  --                   Options processing terminator", file=sys.stderr)
    print(file=sys.stderr)


################################################################################
def _handle_interrupts(signal_number, current_stack_frame):
    """Prevent SIGINT signals from displaying an ugly stack trace"""
    print(" Interrupted!\n", file=sys.stderr)
    _display_help()
    sys.exit(ERROR)


################################################################################
def _handle_signals():
    """Process signals"""
    signal.signal(signal.SIGINT, _handle_interrupts)


################################################################################
def _process_environment_variables():
    """Process environment variables"""
    if "DCMP_DEBUG" in os.environ:
        logging.disable(logging.NOTSET)


################################################################################
def _process_command_line():
    """Process command line options"""
    # pylint: disable=C0103 disable=W0622
    global parameters
    # pylint: enable=C0103 enable=W0622

    # option letters followed by : expect an argument
    # same for option strings followed by =
    character_options = "hsv?"
    string_options = [
        "debug",
        "dedup",
        "help",
        "nosymlinks",
        "quiet",
        "silent",
        "verbose",
        "version",
    ]

    try:
        options, remaining_arguments = getopt.getopt(
            sys.argv[1:], character_options, string_options
        )
    except getopt.GetoptError as error:
        logging.critical("Syntax error: %s", error)
        _display_help()
        sys.exit(ERROR)

    for option, _ in options:

        if option == "--dedup":
            parameters["Dedup mode"] = True
            # Let's be cautious against symlink attacks:
            parameters["Follow symlinks"] = False

        elif option in ("-h", "--nosymlinks"):
            parameters["Follow symlinks"] = False

        elif option in ("-s", "--silent", "--quiet"):
            parameters["Silent mode"] = True

        elif option in ("-v", "--verbose"):
            parameters["Verbose mode"] = True

        elif option == "--debug":
            logging.disable(logging.NOTSET)

        elif option in ("--help", "-?"):
            _display_help()
            sys.exit(OK)

        elif option == "--version":
            print(ID.replace("@(" + "#)" + " $" + "Id" + ": ", "").replace(" $", ""))
            sys.exit(OK)

    logging.debug("_process_command_line(): parameters:")
    logging.debug(parameters)
    logging.debug("_process_command_line(): remaining_arguments:")
    logging.debug(remaining_arguments)

    return remaining_arguments


################################################################################
def _hash_file(filename):
    """Hash a file using SHA-256 and return its hexadecimal digest"""
    file_hash = hashlib.sha256()
    if os.path.isfile(filename):
        with open(filename, 'rb') as file:
            block = file.read(BLOCK)
            while len(block) > 0:
                file_hash.update(block)
                block = file.read(BLOCK)

    return file_hash.hexdigest()


################################################################################
def main():
    """The program's main entry point"""
    program_name = os.path.basename(sys.argv[0])

    _initialize_debugging(program_name)
    _handle_signals()
    _process_environment_variables()
    arguments = _process_command_line()

    if len(arguments) != 2:
        logging.critical("Syntax error: expecting 2 arguments")
        _display_help()
        sys.exit(ERROR)

    if not os.path.isdir(arguments[0]) or not os.path.isdir(arguments[1]):
        print("ERROR: arguments must be directories")
        logging.critical("Syntax error: arguments must be directories")
        _display_help()
        sys.exit(ERROR)

    exit_status = SAME

    dir1 = arguments[0]
    if dir1.endswith(os.sep):
        dir1 = re.sub(os.sep + "$", "", dir1)
    elif os.altsep is not None and dir1.endswith(os.altsep):
        dir1 = re.sub(os.altsep + "$", "", dir1)

    dir2 = arguments[1]
    if dir2.endswith(os.sep):
        dir2 = re.sub(os.sep + "$", "", dir2)
    elif os.altsep is not None and dir2.endswith(os.altsep):
        dir2 = re.sub(os.altsep + "$", "", dir2)

    for root1, dirs1, files1 in os.walk(dir1, followlinks=parameters["Follow symlinks"]):
        path2 = dir2 + re.sub("^" + dir1, "", root1)

        root2 = ""
        dirs2 = []
        files2 = []
        for root2, dirs2, files2 in os.walk(path2, followlinks=parameters["Follow symlinks"]):
            break

        for directory in dirs1:
            if directory in dirs2:
                if parameters["Verbose mode"]:
                    print(IDENTICAL + " " + root1 + os.sep + directory)
            else:
                if parameters["Silent mode"]:
                    sys.exit(DIFFERENCES)
                else:
                    print(MISSING_IN_DIR2 + " " + root1 + os.sep + directory)
                    exit_status = DIFFERENCES

        for directory in dirs2:
            if directory not in dirs1:
                if parameters["Silent mode"]:
                    sys.exit(DIFFERENCES)
                else:
                    print(MISSING_IN_DIR1 + " " + root2 + os.sep + directory)
                    exit_status = DIFFERENCES

        for file in files1:
            file1 = root1 + os.sep + file
            if file in files2:
                file2 = root2 + os.sep + file

                if os.path.islink(file1):
                    if os.path.islink(file2) and os.path.readlink(file1) == os.path.readlink(file2):
                        if parameters["Verbose mode"]:
                            print(IDENTICAL + " " + file1)
                        if parameters["Dedup mode"]:
                            try:
                                os.remove(file1)
                                logging.info("Removed symlink: %s", file1)
                            except:
                                logging.error("Failed removing symlink: %s", file1)
                    else:
                        if parameters["Silent mode"]:
                            sys.exit(DIFFERENCES)
                        else:
                            print(DIFFERENT + " " + file1)
                            exit_status = DIFFERENCES
                elif _hash_file(file1) == _hash_file(file2):
                    if parameters["Verbose mode"]:
                        print(IDENTICAL + " " + file1)
                    if parameters["Dedup mode"]:
                        try:
                            os.remove(file1)
                            logging.info("Removed file: %s", file1)
                        except:
                            logging.error("Failed removing file: %s", file1)
                else:
                    if parameters["Silent mode"]:
                        sys.exit(DIFFERENCES)
                    else:
                        print(DIFFERENT + " " + file1)
                        exit_status = DIFFERENCES
            else:
                if parameters["Silent mode"]:
                    sys.exit(DIFFERENCES)
                else:
                    print(MISSING_IN_DIR2 + " " + file1)
                    exit_status = DIFFERENCES

        for file in files2:
            if file not in files1:
                if parameters["Silent mode"]:
                    sys.exit(DIFFERENCES)
                else:
                    print(MISSING_IN_DIR1 + " " + root2 + os.sep + file)
                    exit_status = DIFFERENCES

    if parameters["Dedup mode"]:
        for root1, dirs1, files1 in os.walk(
            dir1,
            topdown=False,
            followlinks=parameters["Follow symlinks"]
        ):
            dir_removed = False
            try:
                os.removedirs(root1)
                dir_removed = True
            except:
                pass
            if dir_removed:
                logging.info("Removed empty dir: %s", root1)

    sys.exit(exit_status)


if __name__ == "__main__":
    main()
