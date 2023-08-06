"""
Module for Bar classes.
"""

from typing import List, Tuple

import pygame

from pyggui.gui.item import StaticItem, Item
from pyggui.gui.text import Text


class DefaultProgressBar(StaticItem):
    """
    Default progress bar is a horizontal rectangle that gets filled up based on progress.
    The default color is white but can be changed by modifying the color attribute.
    update_progress(float) method should be used to update the fill of bar.
    """
    def __init__(self,
                 position: List[int] = [0, 0],
                 size: Tuple[int, int] = (1, 1),
                 visible: bool = True,
                 selected: bool = False,
                 color: Tuple[int, int, int] = (255, 255, 255),
                 line_width: int = 3
                 ):
        """
        Args:
            position (List[int]): Position of bar on screen or page.
            size (Tuple[int, int]): Total size of bar.
            visible (bool): If currently visible.
            selected (bool): If currently selected.
            color (Tuple[int, int, int]): Color of bar outline and fill.
            line_width (int): Line width of bar outline.
        """
        super().__init__(position, size, visible, selected)
        self.color = color
        self.line_width = line_width
        self._progress = 0
        self.progress_length = 1  # Between 1 and self.width
        self.progress_rect = pygame.Rect(self.x, self.y, self.progress_length, self.height)
        self.update_progress(0)

    @property
    def progress(self):
        return self._progress

    def update_progress(self, progress: float) -> None:
        """
        Args:
            progress (float): Float representation of current progress in range [0, 1]. Progress bar is filled
                based on this value; 0 = empty, 0.5 = half full, 1 = full.
        """
        # First update progress rect position
        self.progress_rect.x = self.x
        self.progress_rect.y = self.y
        progress = min(1, max(0, progress))  # Put progress in between 0 and 1
        self._progress = progress
        self.progress_length = int(self.width * progress)
        self.update()

    def update(self) -> None:
        """
        Method updates current filling bar.
        """
        self.progress_rect.width = self.progress_length

    def draw(self):
        """
        Method draws self to screen.
        """
        if self.visible:
            # Draw outline of bar
            pygame.draw.rect(
                self.display,
                self.color,
                self.rect,
                self.line_width
            )
            # Draw progress filled rectangle
            pygame.draw.rect(
                self.display,
                self.color,
                self.progress_rect,
                0
            )  # Pass 0 width -> fill rectangle


class ProgressBar(StaticItem):
    """
    Progress bar is used for displaying progress. Passing a directory path in the argument directory_path will let
    you create a custom imaged progress bar, an DefaultProgressBar gets returned otherwise, for wich size should be
    passed.
    """
    def __new__(cls, *args, **kwargs):
        # Check if directory_path was passed
        kwargs_copy = kwargs.copy()  # Mutate copy so all kwargs still go through
        directory_path = kwargs_copy.pop("directory_path", False)
        if directory_path:
            # Created instance of self is returned
            return super(ProgressBar, cls).__new__(cls, *args, **kwargs)
        else:
            # Return default Loading Bar otherwise
            return DefaultProgressBar(*args, **kwargs)

    def __init__(
        self,
        position: List[int] = [0, 0],
        size: Tuple[int, int] = (1, 1),
        visible: bool = True,
        selected: bool = False,

    ):
        super().__init__(position, size, visible, selected)
        # TODO: Implement Imaged progress bar
