"""
Module for building assets objects used in Game object.
"""

import os
import inspect
from typing import Dict, List, Union

from pyggui.exceptions import AssetsDirectoryNotDefinedError, AssetDoesNotExistError


class Directory:
    """
    Class for building directory objects. Every directories file and sub-directory can be accessed through attributes,
    if the file/directory does not exist the AssetDoesNotExistError gets raised.

    Properties:
        files: Returns a list of file paths of files contained in the directory.
        directories (List[]): Returns a list of directory paths of sub-directories.
        empty (bool): If directory is empty.
        path (str): Will return the directories path.

    Directory can be iterated through every one of its contents, where sub-directories come first and files second.
    Printing out the object will output its structure.
    TODO: Implement repr method.
    """
    def __init__(self, directory_structure: Dict):
        """
        Args:
            directory_structure (Dict): Dictionary containing information of subdirectories and files.
        """
        self.directory_structure = directory_structure

        self._files = []
        if "_files" in self.directory_structure:
            self._files = [value["_path"] for value in self.directory_structure["_files"].values()]
        self._directories = []
        # Create directories list, long way without list comprehension, it's more readable
        for key, value in self.directory_structure.items():
            if key != "_path" and "_path" in value:
                self.directories.append(value["_path"])

    @property
    def files(self) -> List[str]:
        return self._files

    @property
    def directories(self) -> List[str]:
        return self._directories

    @property
    def empty(self) -> bool:
        return not ((self._files != []) and (self._folders != []))

    def __getattr__(self, attr):
        if attr in self:
            getattr(self, attr)
        else:
            # Raise error otherwise
            asset_path = self.directory_structure["_path"] + "\\" + attr
            message = f"The asset {asset_path} does not exist in the defined assets directory."
            raise AssetDoesNotExistError(message)

    def __iter__(self):
        for directory in self._directories:
            yield directory
        for file in self._files:
            yield file


def build_directory(directory_structure: Dict) -> Directory:
    """
    Function builds directory object by setting it appropriate attributes, sub-directories get also added as
    attributes and recursively built.

    Args:
        directory_structure (Dict): Dictionary containing structure, created inside the AssetBuilder.build method.

    Returns:
        Directory: Object.
    """
    parent_directory = Directory(directory_structure)

    def build(dir_structure, directory):
        setattr(directory, "path", dir_structure["_path"])
        for attr in directory.directory_structure:  # If sub-directory, set new sub-Directory object
            if attr != "_path" and attr != "_files":
                child_dir = Directory(directory_structure=dir_structure[attr])  # Make object
                setattr(directory, attr, child_dir)  # Set is as an attribute
                build(directory.directory_structure[attr], child_dir)  # Recursive build child
        if "_files" in dir_structure:  # If file, return file path
            for attr in directory.directory_structure["_files"]:
                setattr(directory, attr, dir_structure["_files"][attr]["_path"])

    build(directory_structure, parent_directory)

    return parent_directory


class Assets:
    """
    Dummy class for raising error (when fetching attribute) when Asset directory was not defined.
    """
    def __init__(self):
        self.directory_structure = None

    def __getattr__(self, attr):
        message = "The Asset directory was not defined in the initialization of Game object. " \
                      "Set: assets_directory = path/to/your/assets/folder."
        raise AssetsDirectoryNotDefinedError(message)

    def __repr__(self):
        return "Asset directory was not defined. Define it passing assets_directory to the Game object."


class AssetBuilder:
    """
    Class used for building the Directory object.
    """
    def __init__(self, directory: str = None):
        """
        Args:
            directory (str): Path to assets directory.
        """
        # Check directory argument
        if not directory:  # If not passed grab modules parent directory
            self.directory_path = None
        else:
            self.directory_path = os.path.normpath(directory)  # Normalize path

    def build(self) -> Dict:
        """
        Method will build and return the correct object for using assets in game. If path was not defined the
        dummy Asset object gets returned, so if access to some file is attempted an error gets returned.
        """
        if not self.directory_path:  # Return dummy object if path was not given
            return Assets()

        norm_dir_path = os.path.normpath(self.directory_path)  # Normalize path
        main_structure = {"_path": norm_dir_path}  # Main mutable dictionary that will get returned

        def traverse(structure: Dict, directory: str) -> None:
            """
            Recursive function goes over directory, adding its files in the structure key = 'files' list,
            recursive call for each directory found.
            """
            for name, full_path in [(path, os.path.join(directory, path)) for path in os.listdir(directory)]:
                # If file
                if os.path.isfile(full_path):  # Add each file to files key in structure
                    if "_files" not in structure:
                        structure["_files"] = {}  # Empty dict
                    name_split = name.split(".")  # Get file name and extension
                    _name, _extension = name_split[0], name_split[1]
                    structure["_files"][_name] = {"_extension": _extension, "_path": full_path}
                # If directory
                if os.path.isdir(full_path):  # Add new structure under basename, recursive call
                    basename = os.path.basename(full_path)
                    structure[basename] = {"_path": full_path}
                    traverse(structure[basename], full_path)

        # Call function
        traverse(main_structure, norm_dir_path)
        # Return directory object
        return build_directory(main_structure)
