"""
Module for text based items.
"""

from typing import List, Tuple
import pkg_resources

import pygame

from pyggui.gui.item import StaticItem
from pyggui.helpers.helpers import create_object_repr


class Text(StaticItem):
    """
    Class for displaying text on screen. You can pass own font file or use one of the System specific ones by passing a
    font name without any . / characters.
    Text can not be resized after initialization, for that use the ResizableText class TODO(Add).

    Note: If you change the value of the text the render method should be called to re-render the changed text.
    """
    def __init__(self,
                 position: List[int] = [0, 0],
                 value: str = "Text",
                 font: str = None,
                 font_size: int = 21,
                 color: Tuple[int, int, int] = (255, 255, 255)
                 ):
        """
        Args:
            position (List[int]): Position of text object on screen or page.
            value (str): Value of text (actual displayed text)
            font (str): System specific font or path to font file to use.
            font_size (int): Size of displayed text
            color (tuple[int, int, int]): Color of displayed text
        """
        pygame.font.init()  # Init font
        # Set color and text
        self.color = color
        self._value = value
        self.font_size = font_size
        # If font not passed use default font, load with pkg_resources so no problems arise in packaging
        if not font:
            font = pkg_resources.resource_filename("pyggui.defaults.assets.fonts", "retro_gaming.ttf")
        # Check font type, if system specific or file
        if "\\" in font or "." in font:  # If passed font string has / or . it is a path to font file
            self.font = pygame.font.Font(font, font_size)
        else:
            self.font = pygame.font.SysFont(font, font_size)
        # Get size of of rendered font, create surface
        size = self.font.size(value)
        self.surface = self.font.render(value, True, self.color)
        # Call to super method with new fetched size of surface
        super().__init__(position, size)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val: str):
        self._value = val
        self.render()

    def render(self) -> None:
        """  TODO: Add value property and setter to auto-update text
        Method re-renders the text surface, method should be called once the text value has changed.
        """
        self.surface = self.font.render(self._value, True, self.color)
        self.size = self.font.size(self._value)

    def update(self) -> None:
        """
        Method will update all items attached to self.
        """
        for item in self.items:
            item.update()

    def draw(self) -> None:
        """
        Method will draw text and all attached items on screen.
        """
        self.display.blit(self.surface, self.position)
        for item in self.items:
            item.draw()

    def __repr__(self) -> str:
        return create_object_repr(self)
