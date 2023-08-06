"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -m pyggui` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``pyggui.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``pyggui.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import sys
import os
import shutil

from pyggui.defaults import structures  # Import the structures package so we can fetch its path
from pyggui.client.make import main as make_main
from pyggui.client.build import main as build_main


def main(argv=sys.argv):
    """
    Creates a base directory structure for your project / game.

    Args:
        argv (list): List of arguments

    Returns:
        int: A return code
    """
    exit_code = 0
    if "build" in argv:
        argv.remove("build")
        exit_code = build_main(argv)
    elif "make" in argv:
        argv.remove("make")
        exit_code = make_main(argv)
    else:
        print("PyGgui: No parameters specified. Pass either make or build as arguments.")

    return exit_code
