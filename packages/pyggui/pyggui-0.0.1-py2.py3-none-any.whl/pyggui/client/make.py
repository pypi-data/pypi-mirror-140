"""
Module for copying basic game structure into users directory.
"""

from typing import List
import sys
import os
import shutil

from pyggui.defaults import structures  # Import the structures package so we can fetch its path

IGNORE = ["__pycache__", ".ignore"]


def find_environment_directory(path: str) -> str:
    """
    Function finds venv in passed path and returns path to its parent directory. If venv or env not found, returns
    None.

    Args:
        path (str): Path to find venv or env in.
    """
    path_list = path.split(os.sep)
    venv_dir = []
    for i, _dir in enumerate(path_list):
        if _dir in ["venv", "env"]:
            break
        elif i == len(path_list) - 1:
            return None
        else:
            venv_dir.append(_dir)

    return os.sep.join(venv_dir)


def copy_folder(from_dir: str, to_dir: str, indent: int) -> None:
    """
    Function copies one directory to another with all its contents.
    Prints what was copied, each sub-directory gets more indented.

    Args:
        from_dir (str): Path to directory to copy.
        to_dir (str): Path to directory where to copy.
        indent (int): Amount to indent, used in recursion.
    """
    for file_name in os.listdir(from_dir):
        for ignored in IGNORE:
            if ignored in file_name:
                continue
        if file_name not in IGNORE:
            from_file_path = os.path.join(from_dir, file_name)
            to_file_path = os.path.join(to_dir, file_name)
            if os.path.isdir(from_file_path):  # If folder, recursive call
                if not os.path.isdir(to_file_path):  # Make dir if not exists
                    os.mkdir(to_file_path)
                print((indent * 4) * " " + f"Copying: {file_name}/")
                copy_folder(from_file_path, to_file_path, indent=indent+1)
            if os.path.isfile(from_file_path):
                print((indent * 4) * " " + f"Copying: {file_name}")
                shutil.copy(from_file_path, to_file_path)


def copy_structure(from_dir: str, to_dir: str) -> None:
    """
    Function copies one structure to the next without copying already set directories / files.

    Args:
        from_dir (str): Path to directory to copy
        to_dir (str): Path to directory where to copy
    """
    indent = " " * 4
    print("PyGgui: Creating your project...")
    for item in os.listdir(from_dir):
        item_from_path = os.path.join(from_dir, item)
        item_end_path = os.path.join(to_dir, item)
        if item not in IGNORE:
            if os.path.isfile(item_from_path):
                # Check if that file does not exist -> copy it
                if not os.path.isfile(item_end_path):
                    print(indent + f"Copying: {item}")
                    shutil.copy(item_from_path, item_end_path)
                else:
                    print(indent + f"File {item} already exists, skipping.")
            if os.path.isdir(item_from_path):
                if not os.path.isdir(item_end_path):
                    os.mkdir(item_end_path)
                    print(indent + f"Copying: {item}/")
                    copy_folder(item_from_path, item_end_path, indent=2)
                else:
                    print(indent + f"Directory {item}/ already exists, skipping.")


def main(argv: List[str]) -> int:
    """
    Main function for creating the structure needed to start developing a game using pyggui.

    Args:
        argv (List[str]): sys.argv, not including "make".

    Returns:
        int: Exit code
    """
    base_structure_path = os.path.join(structures.PATH, "base")  # Absolute path of base structure directory
    call_path = argv[0]  # Get path of where call originated from, either some sort of venv or pythons path

    # Update arguments, create argument dictionary
    argv = argv[1:]
    argument_dict = {
        "-t": None,
        "-p": None
    }
    # Parse args into argument dictionary
    for arg in argv:
        if "=" in arg:
            split_arg = arg.split("=")
            argument_dict[split_arg[0]] = split_arg[1]

    # Check arguments are okay
    # Check path
    if not argument_dict["-p"]:  # If no path passed to create the structure in, try fetching venv position
        venv_parent_path = find_environment_directory(call_path)
        if not venv_parent_path:
            print("No directory path was specified and the call did not originate from inside a venv. "
                  "Pass a path by the -p argument; ex.: -p=some/path/to/directory, or call from inside a virtual "
                  "environment.")
            return 1
        else:
            argument_dict["-p"] = venv_parent_path

    # Type of structure to copy, currently only base is implemented
    argument_dict["-t"] = base_structure_path

    # Start copying files from specified type of directory into set directory.
    copy_structure(from_dir=argument_dict["-t"], to_dir=argument_dict["-p"])
    print("All done!")
    return 0
