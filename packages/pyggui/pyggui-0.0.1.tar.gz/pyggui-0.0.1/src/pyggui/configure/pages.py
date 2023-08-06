"""
Module used for setting up page classes and page-holding modules throughout directory.
Ultimately the functions used here are used for importing all modules that contain classes that inherit from one parent
class of the _pyggui.gui.page module. This is then used by the controller class to fetch all Page type classes.
"""

from typing import Dict, List
import os
import sys
import inspect
import glob
import importlib
import pkgutil

from pyggui.configure.build import update_config_file

ignore_directories = ["venv", "env"]


def get_all_page_classes() -> Dict[str, any]:
    """
    Function returns a dictionary containing all classes that:
        Are imported and are subclasses of classes defined in the _pyggui.gui.page module

    Returns:
        dict[str, any]: Where: key = str(name_of_class), value = class.
    """
    # Fetch all classes defined in the _pyggui.gui.page.py module, save all of its subclasses that are imported
    pages = {}  # Create dictionary with each classes name str as key, class as value
    for name, cls in inspect.getmembers(sys.modules["pyggui.gui.page"]):  # Get members of each module
        if inspect.isclass(cls):  # Filter only classes
            for _class in cls.__subclasses__():  # Fetch subclasses
                pages[str(_class.__name__)] = _class
    return pages


def create_module_import_string(package_name: str, module_path: str) -> str:
    """
    Function creates a module import string (ex. foo.bar.module) based on the package name and file path of python
    file.
    Import string will be created from the package_name ahead (not including package name at beginning).

    Args:
        package_name (str): Name of package where the python module is contained (root. dir. of project).
        module_path (str): Absolute path of module.

    Returns:
        str: Module import string
    """
    relative_file_path = os.path.normpath(module_path)  # Normalize path string into proper os path string
    # Create list with directory names, split at os separator, use lambda to remove .py from file names
    path_list = list(map(
        lambda name: name.replace(".py", "") if ".py" in name else name,
        relative_file_path.split(os.sep)
    ))
    # Check if passed module is from package
    if package_name not in path_list:
        return  # Raise error here
    # Get index of package, return import string from package name on
    package_root_index = path_list.index(package_name)
    return ".".join(path_list[package_root_index + 1:])


def get_all_page_import_strings(dir_path: str, called_from_module: str) -> List[str]:
    """
    Function reads and creates all needed import strings in the directory structure except the called_from_module.

    Args:
        dir_path (str): Directory root to import all modules from its structure.
        called_from_module (str): Absolute path of module where call originated (main module), will be ignored.
    """
    import_strings = []
    # Get directory of module the call originated from
    package_name = os.path.basename(os.path.dirname(called_from_module))
    # Traverse directory structure, ignore some directories
    for root, directories, files in os.walk(dir_path):
        directories[:] = [d for d in directories if d not in ignore_directories]
        for filename in files:
            # Only use .py files and exclude files starting with __ (such as __init__)
            if filename.endswith(".py") and not filename.startswith("__"):
                file_path = os.path.join(root, filename)
                # Check file is not the one where the call originated from (this would cause double imports)
                if not os.path.samefile(file_path, called_from_module):
                    # Create module-import string and import the module
                    import_strings.append(create_module_import_string(package_name, os.path.join(root, filename)))
    return import_strings


def import_all_modules(dir_path: str, called_from_module: str) -> None:
    """
    Function imports all modules in the directory structure except the called_from_module.

    Args:
        dir_path (str): Directory root to import all modules from its structure.
        called_from_module (str): Absolute path of module where call originated (main module), will be ignored.
    """
    import_strings = get_all_page_import_strings(dir_path, called_from_module)

    for import_string in import_strings:
        importlib.import_module(import_string)

    # Save import strings into the config.json file located in the (newly created) build directory in the curr. proj.
    dir_path = os.path.dirname(called_from_module)
    config_dict = {
        "imports": import_strings,
        "project_path": dir_path
    }
    update_config_file(dir_path=dir_path, data=config_dict)


def setup(call_from: inspect.FrameInfo, directory: str = None) -> None:
    """
    Function imports all modules in the directory. If directory is not passed it will import all modules in the
    directory where the call originated from i.e. call_from modules parent directory.
    Function should be used for importing modules of type page, i.e. modules containing classes that inherit from Page,
    or any other class defined in the _pyggui.gui.page module.

    Args:
        call_from (inspect.FrameInfo): FrameInfo object where the call originated from, this object should be fetched
            from inspect.stack() when calling function, in argument.
        directory (str): Absolute or relative path of directory to search and import modules.
    """
    module_file = inspect.getmodule(call_from[0]).__file__  # Get module file where call originated from
    # Check directory argument
    if not directory:  # If not passed grab modules parent directory
        directory = os.path.dirname(module_file)
    elif not os.path.isabs(directory):  # If passed as relative, join with directory of module
        directory = os.path.join(os.path.dirname(module_file), directory)
    directory = os.path.normpath(directory)  # Normalize path
    # Import all modules except the one where the call originated from
    import_all_modules(dir_path=directory, called_from_module=module_file)
