"""
Module for anything related to files
"""

from __future__ import annotations
from typing import Callable, List, Tuple, Dict, Union
import os
import time
import json

import pygame


class ImageLoader:
    @staticmethod
    def load_image(image_path: str) -> pygame.surface.Surface:
        """
        Method loads given path into image.

        Args:
            image_path (str): Path to image to load

        Returns:
            pygame.surface.Surface: Image loaded as a Pygame surface
        """
        return pygame.image.load(image_path).convert()  # .convert() optimizes speed by 5x

    @staticmethod
    def load_transparent_image(image_path: str) -> pygame.surface.Surface:
        """
        Method loads given path into transparent image.

        Args:
            image_path (str): Path to image to load

        Returns:
            pygame.surface.Surface: Image loaded as a Pygame surface
        """
        return pygame.image.load(image_path).convert_alpha()  # .convert() optimizes speed by 5x

    @staticmethod
    def load_folder(folder_path: str) -> List[pygame.surface.Surface]:
        """
        Method loads all ImageLoader from the folder intro a sprite list.

        Args:
            folder_path (str): Path to folder to load images from

        Returns:
            list[pygame.surface.Surface]: List containing Pygame images loaded as surfaces
        """
        image_list = []
        for image_path in os.listdir(folder_path):
            path = os.path.join(folder_path, image_path)
            image_list.append(ImageLoader.load_image(path))
        return image_list

    @staticmethod
    def load_transparent_folder(folder_path: str) -> List[pygame.surface.Surface]:
        """
        Method loads all ImageLoader from the folder intro a sprite list.

        Args:
            folder_path (str): Path to folder to load images from

        Returns:
            list[pygame.surface.Surface]: List containing Pygame images loaded as surfaces
        """
        image_list = []
        for image_path in os.listdir(folder_path):
            path = os.path.join(folder_path, image_path)
            image_list.append(ImageLoader.load_transparent_image(path))
        return image_list


class DirectoryReader:
    """
    Class consisting of static methods for reading directories. Used for fetching sub-directories, all files, the
    directories structure, etc.
    """
    @staticmethod
    def get_all_directories(dir_path: str) -> List[Tuple[str, str]]:
        """
        Method finds all sub-directories in the given directory.

        Args:
            dir_path (str): Path to directory to search from

        Returns:
            List[Tuple[str, str]]: List of tuples (directory name, directory path).
        """
        folder_list = []
        for item in os.scandir(dir_path):
            if item.is_dir():
                folder_list.append((item.name, os.path.abspath(item.path)))
        return folder_list

    @staticmethod
    def get_all_files(dir_path: str) -> List[Tuple[str, str]]:
        """
        Method finds all file names and its paths in the given directory.

        Args:
            dir_path (str): Path to directory to search from

        Returns:
            List[Tuple[str, str]]: List of tuples (file name, file path).
        """
        file_list = []
        for item in os.scandir(dir_path):
            if item.is_file():
                file_list.append((item.name, os.path.abspath(item.path)))  # Append tuple
        return file_list

    @staticmethod
    def get_structure(dir_path: str) -> Dict[str, Union[str, List, Dict]]:
        """
        Method goes over the passed directory and creates a special structured dictionary.

        Created dictionary follows this rules:
            * For each directory create a sub-dictionary under the directories name as the key,
            * Each file in giver directory is added in a list under 'files' key, file gets added as a tuple where
                first value is the files name, second value its relative path based on dir_path.
        The above is then run recursively across the directories tree structure.

        Example:
            Passing bottom directory with its relative or absolute path
            Directory:
                button/
                    - normal.png
                    on_click/
                        - 01.png
                        - 02.png
                    on_hover/
                        - 01.png
            Will return dictionary:
                {
                    'path': 'button/'
                    'files': [('normal.png', 'button/normal.png')],

                    'on_click': {
                        'path': 'button/on_click'
                        'files': [
                            ('01.png', 'button/on_click/01.png'),
                            ('02.png', 'button/on_click/02.png')
                            ]
                    },

                    'on_hover': {
                        'path': 'button/on_hover',
                        'files': [
                            ('01.png', 'button/on_hover/01.png')
                        ]
                    }
                }


        Args:
            dir_path (str): Directory path to traverse and create structure from.

        Returns:
            Dict[str, Union[str, List, Dict]]: Structured dictionary.
        """
        norm_dir_path = os.path.normpath(dir_path)  # Normalize path
        main_structure = {"path": norm_dir_path}  # Main mutable dictionary that will get returned

        def traverse(structure: Dict, directory: str) -> None:
            """
            Recursive function goes over directory, adding its files in the structure key = 'files' list,
            recursive call for each directory found.
            """
            for name, full_path in [(path, os.path.join(directory, path)) for path in os.listdir(directory)]:
                # If file
                if os.path.isfile(full_path):  # Add each file to files key in structure
                    if "files" not in structure:
                        structure["files"] = []
                    structure["files"].append((name, full_path))
                # If directory
                if os.path.isdir(full_path):  # Add new structure under basename, recursive call
                    basename = os.path.basename(full_path)
                    structure[basename] = {"path": full_path}
                    traverse(structure[basename], full_path)
        # Call function
        traverse(main_structure, norm_dir_path)
        return main_structure


class Json:
    """
    Class for loading, writing and updating data in json files.
    All json files must contain dictionaries as the main scope object.
    """
    @staticmethod
    def load(path: str) -> Union[Dict, List]:
        """
        Method loads a single json file, returning its contents.

        Args:
            path (str): Path to Json file.

        Returns:
            Union[Dict, List]: Content of the Json file
        """
        try:
            with open(path, "r") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"Json.load: Unable to find Json file on path:\n    {path}")

    @staticmethod
    def update(path: str, data: Dict) -> Dict:
        """
        Method will update the dictionary with data and return the updated dict.

        Args:
            path (str): Path to Json file.
            data (Dict): Dictionary of key-value pairs to update in the json file

        Returns:
            Dict: Updated dictionary.
        """
        # Read data
        try:
            with open(path, "r") as f:
                read_data = json.load(f)
        except FileNotFoundError:
            print(f"Json.update: Unable to find Json file on path:\n    {path}")
            return
        # Update
        read_data.update(data)
        # Save, at this point we know the path exists
        with open(path, "w") as f:
            json.dump(read_data, f, indent=4)
        return read_data

    @staticmethod
    def save(path: str, data: Dict) -> None:
        """
        Method saves data into a json file specified by passed path.

        Args:
            path (str): Path to Json file to save data to.
            data (Dict): Dictionary to save in the json file.
        """
        # Check if path contains .json
        if not (".json" in path):
            path += ".json"
        # Write data
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
        except FileNotFoundError:
            print(f"Json.save: Unable to find Json file on path:\n    {path}")
            return
