"""
Module for classes handling images.
"""

from typing import List, Tuple, Union

import pygame

from pyggui.gui.item import StaticItem, ResizableItem
from pyggui.helpers.file_handling import ImageLoader
from pyggui.helpers.helpers import create_object_repr


def fetch_image(image: Union[str, pygame.Surface], transparent: bool = False) -> pygame.Surface:
    """
    Function loads one image and returns it as a pygame.Surface object.

    Args:
        image (Union[str, pygame.Surface]): Either a path to the image (preferably relative path), or an already
                loaded image as a pygame.Surface object.
        transparent (bool): If image should be loaded as transparent. If image is passed as a Surface object it
                is set as the default False.

    Returns:
        pygame.Surface: Image loaded into a surface,
    """
    if isinstance(image, pygame.Surface):
        return image  # Passed image is already a pygame.Surface object
    else:
        if transparent:  # Load as transparent
            return ImageLoader.load_transparent_image(image)
        else:  # Load as normal
            return ImageLoader.load_image(image)


class StaticImage(StaticItem):
    """
    Class for handling a single static image. This image can be moved but not resized, refer to ResizableImage for
    resizable images or pass 'resizable=True' to Image class constructor.
    inherits from StaticItem.
    """
    def __init__(self,
                 image: Union[str, pygame.Surface],
                 transparent: bool = False,
                 position: List[int] = [0, 0],
                 visible: bool = True,
                 selected: bool = False,
                 resizable: bool = False,
                 ):
        """
        Args:
            image (Union[str, pygame.Surface]): Either a path to the image (preferably relative path), or an already
                loaded image as a pygame.Surface object.
            transparent (bool): If image should be loaded as transparent. If image is passed as a Surface object it
                is set as the default False.
            position (List[int]): Position of image on screen or Page.
            visible (bool): If image is visible at beginning. Defaults to True.
            selected (bool): If item is selected at beginning. Defaults to False.
            resizable (bool): If image object can be resized. Defaults to False.
        """
        self.resizable: bool = resizable

        self.image = fetch_image(image=image, transparent=transparent)
        self.transparent = transparent

        size = tuple(self.image.get_rect()[2:])
        super().__init__(position, size, visible, selected)

    def draw_at(self, position: List[int]) -> None:
        """
        Method draws Image at given position without drawing all items attached to self.

        Args:
            position (List[int]): Position on screen to draw image at.
        """
        self.display.blit(self.image, position)

    def get(self) -> pygame.Surface:
        """
        Method returns current image.

        Returns:
            pygame.Surface: Current surface where the image is loaded in.
        """
        return self.image

    def draw(self) -> None:
        """
        Used for drawing itself and every item attached to it.
        """
        self.display.blit(self.image, self.position)
        for item in self.items:
            item.draw()

    def __repr__(self) -> str:
        return create_object_repr(self)


class ResizableImage(ResizableItem):
    """
    Class for handling a single static image that can be moved and re-sized.
    Inherits from ResizableItem.
    """
    def __init__(self,
                 image: Union[str, pygame.Surface],
                 transparent: bool = False,
                 position: List[int] = [0, 0],
                 visible: bool = True,
                 selected: bool = False,
                 resizable: bool = True
                 ):
        """
        Args:
            image (Union[str, pygame.Surface]): Either a path to the image (preferably relative path), or an already
                loaded image as a pygame.Surface object.
            transparent (bool): If image should be loaded as transparent. If image is passed as a Surface object it
                is set as the default False.
            position (List[int]): Position of image on screen or Page.
            visible (bool): If image is visible at beginning. Defaults to True.
            selected (bool): If item is selected at beginning. Defaults to False.
            resizable (bool): If image object can be resized. Defaults to False.
        """
        self.resizable = resizable

        self.image = fetch_image(image=image, transparent=transparent)
        self.transparent = transparent

        self.current_image = self.image  # Currently used image

        size = tuple(self.image.get_rect()[2:])
        super().__init__(position, size, visible, selected)  # Initialize parent class with fetched size

    def resize(self, factor: float) -> None:
        """
        Method will re-size image and its position based on a factor passed as argument.

        Args:
            factor (float): Factor to scale item in range [0, inf]
        """
        super(ResizableImage, self).resize(factor)
        self.resized = pygame.transform.scale(self.image, self.resized_size)
        self.current_image = self.resized

    def reset_size(self) -> None:
        """
        Method will reset images size to the initially set one.
        """
        super(ResizableImage, self).reset_size()
        self.current_image = self.image

    def draw(self) -> None:
        """
        Method will draw itself and every item attached to it.
        """
        self.display.blit(self.current_image, self.position)
        for item in self.items:
            item.draw()

    def __repr__(self) -> str:
        return create_object_repr(self)


class Image:
    """
    Class for creating image objects and place them on screen or page.
    Argument 'transparent' decides how the passed image (if passed as a path) will be loaded (as a transparent surface
        or not).
    Class can return either a ResizableImage object or a StaticImage object based on the passed argument 'resizable',
        which defaults to false.
    """
    def __new__(cls, *args, **kwargs):
        kwargs_copy = kwargs.copy()  # Mutate copy so all kwargs go through
        resizable = kwargs_copy.pop("resizable", False)
        # Return correct image object
        if resizable:
            return ResizableImage(*args, **kwargs)
        else:
            return StaticImage(*args, **kwargs)

    def __init__(self,
                 image: Union[str, pygame.Surface],
                 transparent: bool = False,
                 position: List[int] = [0, 0],
                 visible: bool = True,
                 selected: bool = False,
                 resizable: bool = True
                 ):
        """
        Args:
            image (Union[str, pygame.Surface]): Either a path to the image (preferably relative path), or an already
                loaded image as a pygame.Surface object.
            transparent (bool): If image should be loaded as transparent. If image is passed as a Surface object it
                is set as the default False.
            position (List[int]): Position of image on screen or Page.
            visible (bool): If image is visible at beginning. Defaults to True.
            selected (bool): If item is selected at beginning. Defaults to False.
            resizable (bool): If image object can be resized. Defaults to False.
        """
        pass
