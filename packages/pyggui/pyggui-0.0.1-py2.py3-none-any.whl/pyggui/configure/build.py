"""
Module containing functionality for pre-setting build config files, directories, ...
"""

from typing import Dict
import os

from pyggui.helpers import Json


def update_config_file(dir_path: str, data: Dict) -> None:
    """
    Function updates the current config file in the project using this library.
    Where config file is just a config.json file saved in the build directory on the top level of the project.

    Args:
        dir_path (str): Path to projects directory.
        data (Dict): Dictionary of key, value pairs to update in the file.
    """
    build_path = os.path.join(dir_path, "build")
    if not os.path.isdir(build_path):
        os.mkdir(build_path)

    config_file_path = os.path.join(build_path, "configure.json")
    if os.path.isfile(config_file_path):
        Json.update(config_file_path, data)
    else:
        Json.save(config_file_path, data)
