"""
Module containing different buttons.
"""

from typing import Callable, List, Tuple, Union

import pygame

from pyggui.gui.item import Item
from pyggui.gui.text import Text
from pyggui.helpers import DirectoryReader, ImageLoader
from pyggui.gui.animation import Animator
from pyggui.helpers.helpers import create_object_repr


class DefaultButton(Item):
    """
    Default button is used when the user hasn't specified an image for the button itself.
    """
    def __init__(
        self,
        controller: 'Controller',
        position: List[int] = [0, 0],
        size: Tuple[int, int] = (100, 40),
        on_click: Callable = lambda: None,
        text: Union[str, Text] = "Button",
        fill_color: Tuple[int, int, int] = (0, 0, 0),
        border_color: Tuple[int, int, int] = (255, 255, 255),
        movable: bool = False,
        visible: bool = True
    ):
        """
        Args:
            controller (Controller): Main controller object.
            position (List[int]): Position of item on screen (or page). Defaults to [0, 0]
            size (Tuple[int, int]): Size of item. Defaults to (100, 40).
            on_click (Callable): Callable function gets triggered once the button is clicked. Defaults to None.
            text (Union[str, Text]): String or Text object to add as text to button. Defaults to 'Button'.
            fill_color (Tuple[int, int, int]): Inside color of button. Defaults to white.
            border_color (Tuple[int, int, int]): Border color of button, also determines the color of text if text was
                passed as string. Defaults to black.
            movable (bool): If item will be moved by on_click action. Used for slider buttons. Defaults to false.
            visible (bool): If item is currently visible.
        """
        super().__init__(controller, position, size, on_click, movable, visible)

        self.controller = controller

        # Check if passed argument is string => create Text object
        if type(text) is str:
            self.text = Text(
                value=text,
                font_size=16,
            )
        else:
            self.text = text

        # Set colors
        self._fill_color = fill_color  # These ones define the colors
        self._border_color = border_color
        self.fill_color = self._fill_color  # These ones get used
        self.border_color = self._border_color

        # Set position of text and add object to items
        self.text.position = self.get_text_position()
        self.items.append(
            self.text
        )

    def get_text_position(self) -> List[int]:
        """
        Method calculates the position of text inside button to that it is centered.

        Returns:
            list[int, int]: Position of centered text.
        """
        # Center text in button
        x_pos = int((self.x + (self.width * 0.5)) - (self.text.width * 0.5))
        y_pos = int((self.y + (self.height * 0.5)) - (self.text.height * 0.5))
        return [x_pos, y_pos]

    def update(self) -> None:
        """
        Method updates self and re-sets text position.
        """
        if self.visible:
            # Call parent method
            super(self.__class__, self).update()
            # And then re center text
            self.text.position = self.get_text_position()

    def draw(self) -> None:
        """
        Method draws button along with its text on screen.
        """
        if self.visible:
            # Switch colors if hovered
            if self.hovered:
                self.border_color = self._border_color
                self.fill_color = self._fill_color
            else:
                self.border_color = self._fill_color
                self.fill_color = self._border_color

            pygame.draw.rect(
                self.display,
                self.border_color,
                self.rect,
                width=0,
                border_radius=10
            )
            pygame.draw.rect(
                self.display,
                self.fill_color,
                self.rect,
                width=3,
                border_radius=10
            )
            self.text.color = self.fill_color
            self.text.render()
            self.text.update()

            for item in self.items:
                item.draw()

    def __repr__(self) -> str:
        return create_object_repr(self)


class Button(Item):
    """
    Class for creating a button. Button has on_click method which gets triggered once the item is clicked.
    A directory path parameter should be passed for creating button with images, otherwise a DefaultButton is
    created.
    Directory path for button images should be structured:
        /some/path/button/-
                            normal.png  # Image or directory of images
                        on_click/
                        on_hover/
        The on_click and on_hover must be directories even if holding just one file.
    Animation velocity can be changed for each of the above types (normal, on_click or on hover) by accessing buttons
    animated dictionary. The dictionary holds Animator objects with passed images, so for ex.:
    Changing animation velocity to on_click animation:
        animated['on_click'].animation_velocity = 0.7
    Changing animation type is also possible but should be done using Animators set_animation method, ex.:
        animated['on_click'].set_animation('loop')
    """
    def __new__(cls, *args, **kwargs):
        # Check if directory_path was passed
        kwargs_copy = kwargs.copy()  # Mutate copy so all kwargs still go through
        folder_path = kwargs_copy.pop("directory_path", False)
        if folder_path:
            # Created instance of self is passed
            return super(Button, cls).__new__(cls)  # Item has default __new__ constructor, pass it only class
        else:
            # Return default button otherwise
            return DefaultButton(*args, **kwargs)

    def __init__(
        self,
        controller: 'Controller',
        directory_path: str = None,
        position: List[int] = [0, 0],
        size: Tuple[int, int] = None,
        on_click: Callable = None,
        movable: bool = False,
        visible: bool = True,
        animation_velocity: Union[float, int] = 1,
        text: Union[str, Text] = None
    ):
        """
        Args:
            controller (Controller): Main controller object.
            directory_path (str): Path to a structured directory holding button images.
            position (List[int]): Position of button on screen (or page).
            size (Tuple[int, int]): Size of item. Defaults to normal images size if not passed. If size is passed it
                determines the buttons hit-box from its position.
            on_click (Callable): Callable function gets triggered once the button is clicked. Defaults to None.
            movable (bool): If item will be moved by on_click action. Used for slider buttons. Defaults to false.
            visible (bool): If item is currently visible.
            animation_velocity (Union[int, float]): Velocity at which to change the current image index. If set to 1;
                images will be changed at each frame, if set to 0.5; images will be changed every second frame, ...
                Defaults to 1.
        """
        self.directory_path = directory_path
        self.animation_velocity = animation_velocity

        self.images = {
            "normal": [],
            "on_hover": [],
            "on_click": []
        }
        self.animated = {
            "normal": None,
            "on_hover": None,
            "on_click": None
        }
        self.current_state_key = "normal"
        self.image_setup()  # Load images
        self.clicked = False

        self.image_size = tuple(self.images["normal"][0].get_rect()[2:])
        # Set size and call parent innit
        if not size:  # Fetch images size if not passed
            size = self.image_size

        super().__init__(controller, position, size, on_click, movable, visible)

    def image_setup(self):
        """
        Method loads all images in the passed directory_path into the local animated dictionary attribute which is used
        internally for animating the button.
        """
        dir_structure = DirectoryReader.get_structure(self.directory_path)
        # normal image or directory of image is the base needed for operating
        if "normal" in dir_structure:
            for name, path in dir_structure["normal"]["files"]:
                self.images["normal"].append(ImageLoader.load_transparent_image(path))
        else:  # Check under files if a normal.extension exists
            normal_image = [path for name, path in dir_structure["files"] if "normal" in name]
            if normal_image:
                self.images["normal"].append(ImageLoader.load_transparent_image(normal_image[0]))
            else:
                # Raise error if normal was not given
                pass

        if "on_hover" in dir_structure:
            for name, path in dir_structure["on_hover"]["files"]:
                self.images["on_hover"].append(ImageLoader.load_transparent_image(path))
        else:
            self.images["on_hover"] = self.images["normal"]

        if "on_click" in dir_structure:
            for name, path in dir_structure["on_click"]["files"]:
                self.images["on_click"].append(ImageLoader.load_transparent_image(path))
        else:
            self.images["on_click"] = self.images["normal"]

        # Set animated, use Animator objects.
        self.animated["normal"] = Animator(images=self.images["normal"], animation_velocity=self.animation_velocity)
        self.animated["on_hover"] = Animator(images=self.images["on_hover"], animation_velocity=self.animation_velocity)
        self.animated["on_click"] = Animator(images=self.images["on_click"], animation_velocity=self.animation_velocity)

    def update(self):
        """ Overwrite parent method for updating this classes custom attributes.
        Used for updating all items attached to it(sizes, positions, etc.).
        """
        if self.visible:
            self.hovered = self.rect.collidepoint(self.controller.input.mouse_position)
            # Check if mouse was clicked on item, in the interval of the debounce time
            if self.hovered:
                self.current_state_key = "on_hover"
                self.animated["normal"].reset_index()
                # Mouse clicked in set interval
                if self.mouse_clicked and self.debounce_time():
                    self.current_state_key = "on_click"
                    self.clicked = True
                    self.on_click()
                    self.was_pressed = True
            # Mouse was released
            elif not self.mouse_clicked:
                self.was_pressed = False
            # If clicked the on_click animation is ongoing
            if self.clicked:
                self.current_state_key = "on_click"
                if self.animated["on_click"].at_end:
                    self.animated["on_click"].reset_index()
                    self.clicked = False
            # Not hovering anymore
            if not self.hovered:
                self.current_state_key = "normal"
                self.animated["on_hover"].reset_index()
            # If was pressed and mouse is not on the item anymore still call on_click method works if movable = True
            if self.was_pressed and self.movable:  # Only check if item is movable, otherwise get multiple clicks
                self.on_click()
            # Update all items
            for item in self.items:
                item.update()

    def draw(self):
        """ Overwrite parent method.
        Used for drawing itself and every item attached to it.
        """
        if self.visible:
            self.display.blit(self.animated[self.current_state_key].get(), self.position)
            for item in self.items:
                item.draw()

    def __repr__(self) -> str:
        return create_object_repr(self)
