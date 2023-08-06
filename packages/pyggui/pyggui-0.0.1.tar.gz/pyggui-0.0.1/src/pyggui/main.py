"""
Module containing main Game class
"""

import sys
from typing import Tuple
import inspect

import pygame

from pyggui.controller import Controller
from pyggui.input import Input
from pyggui.window import Window
from pyggui.configure import pages as configure_pages
from pyggui.configure import asset_builder as configure_asset_builder


class Game:
    """
    Main class for game, holds every game wide property, setting and the main run loop.
    """
    def __init__(
        self,
        display_size: Tuple[int, int] = (720, 360),
        page_directory: str = None,
        entry_page: str = "_WelcomePage",
        assets_directory: str = None,
        fps: int = 0,
        display: pygame.surface.Surface = None
    ):
        """
        Args:
            display_size (Tuple[int, int]): Size of display in px. Defaults to (720, 360).
            page_directory (str): Absolute or relative path to directory containing pages.
                Defaults to directory of where this object is initialised.
            fps (int): Fps constant for game loop.
            display (pygame.surface.Surface): Pass your own surface as the main game object display.
        """
        pygame.init()  # Init Pygame on import time

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):  # If running from PyInstaller
            # Todo: Implement functionality for running through bundled application
            pass
        else:  # Running from a normal Python process
            # Import all modules containing pages
            configure_pages.setup(inspect.stack()[1], directory=page_directory)
        # Build assets object
        self.assets = configure_asset_builder.AssetBuilder(assets_directory).build()

        # Pygame initial configuration
        if display:
            self._display = display
            self._display_size = display.get_size()
        else:
            self._display = pygame.display.set_mode(display_size, pygame.RESIZABLE)
            self._display_size = display_size

        pygame.display.set_caption("Pygame Window w/pyggui")
        self.clock = pygame.time.Clock()

        # Attributes
        self._fps = fps
        self._dt = 0  # Change of time between seconds
        self.paused = False  # If game is paused
        self.entry_page = entry_page

        # Objects
        self.input = Input(self)
        self.controller = Controller(self)
        self.window = Window(self)

        # Add handler object for screen re-size
        self.input.add_event_type_handler(
            event_type=pygame.VIDEORESIZE,
            handler=self.display_resize_handler
        )

    @property
    def display(self):
        return self._display

    @property
    def display_size(self):
        return self._display_size

    @property
    def dt(self) -> float:
        """
        Difference in time (milliseconds) between current frame and previous frame.
        """
        return self._dt

    @property
    def dt_s(self) -> float:
        """
        Difference in time (seconds) between current frame and previous frame.
        """
        return self._dt * 0.001

    @property
    def fps(self) -> float:
        """
        Current FPS the game is running at.
        """
        return round(1000 / self._dt)

    @fps.setter
    def fps(self, frame_rate: int) -> None:
        """
        Cap FPS of game at given integer value.
        """
        self._fps = int(frame_rate)

    def display_resize_handler(self, event) -> None:
        """
        Handler updates the display and its size once the display window has been re-sized.
        """
        self._display_size = (event.w, event.h)
        self._display = pygame.display.set_mode(self.display_size, pygame.RESIZABLE)

    def run(self) -> None:
        """
        Run main game loop. Will update Window, Input and grab time passed from previous frame.
        Loop ends if Input.update returns False i.e. a quit event appeared.
        """
        running = True
        while running:
            self.window.update()
            running = self.input.update()
            self._dt = self.clock.tick(self._fps)
