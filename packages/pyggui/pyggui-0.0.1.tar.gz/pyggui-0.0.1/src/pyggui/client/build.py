"""
Module for building current game into an executable using pyinstaller.
"""

from typing import List, Dict
import os

import PyInstaller.__main__

from pyggui.configure.pages import get_all_page_import_strings
from pyggui.client.make import find_environment_directory
from pyggui.helpers.file_handling import Json


def get_arguments_dict(args: List[str], separator: str = "=") -> Dict:
    """
    Function parses arguments from an args list, based on a separator, into a dictionary of key, value pairs.
    Default separator is '='.

    Args:
        args (List[str]): Arguments list.
        separator (str): Separator for every argument, key'sep'value. Defaults to '='.
    """
    args_dict = {}
    for arg in args:
        split_arg = arg.split(separator)
        if len(split_arg) == 2:
            args_dict[split_arg[0]] = split_arg[1]
    return args_dict


def check_arguments(project_path: str, args_dict: Dict[str, str]) -> str:
    """
    Function checks if the build path, arguments are valid for building with PyInstaller.

    Args:
        project_path (str): Path to the project directory.
        args_dict (Dict[str]): Dictionary holding arguments passed from the console separated by '='.
    Returns:
        False or the path to build config json file.
    """
    if not project_path:
        if "-p" not in args_dict:
            print("Unable to find project directory, run from inside a venv or pass the path to the project root using "
                  "the -p argument, ex.: -p=path/to/myProject")
            return False
        else:
            project_path = args_dict["-p"]
            if not os.path.isdir(project_path):
                print("Invalid project root path, path is either not a directory path or not a valid one.")
                return False
    # Path of generated config.json file while running the game
    build_config_path = os.path.join(project_path, "build/configure.json")
    if not os.path.isfile(build_config_path):
        print(f"Unable to find {build_config_path}, used for running PyInstaller. Run the game to re-make it.")
        return False

    return build_config_path


def create_pyinstaller_command_list(project_path: str, pyggui_directory_path: str, modules_needed: List[str]):
    # TODO:
    # Update the config file for use with Analysis object running thought PyInstaller:
    #   Set the datas and hidden imports parameters.
    #   Create object here and export?
    command_list = [os.path.join(project_path, "main.py")]
    # Add hidden imports commands
    for module_import in modules_needed:
        command_list.append("--hidden-import=" + module_import)
    # Add asset files
    command_list.append("--add-data=" + os.path.join(project_path, "assets") + os.pathsep + "assets")
    return command_list


def main(argv: List[str]) -> int:
    """
    Main function for building the game project into an executable using Pyinstaller.

    Args:
        argv (List[str]): sys.argv, not including "build".

    Returns:
        int: Exit code
    """
    call_path = argv[0]  # Get path of where call originated from, either some sort of venv or a python path
    pyggui_path = os.path.dirname(call_path)
    args_dict = get_arguments_dict(args=argv)
    project_path = find_environment_directory(call_path)
    # Get build path while checking arguments
    build_path = check_arguments(project_path, args_dict)

    if not build_path:
        return

    modules = Json.load(build_path)["imports"]  # Get needed modules list

    # Call run_pyinstaller
    arguments = create_pyinstaller_command_list(project_path, pyggui_path, modules)

    PyInstaller.__main__.run(arguments)
    return 0
