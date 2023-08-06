"""
Module for animation classes that hold image lists and handle different types of animations.
"""

from typing import List, Union


class Animator:
    """
    Class for handling animations in lists of images, can either loop indefinitely or loop once and stay at the last
    image.
    The get method should be called for fetching current image. That method also updates the state of the animator
    object, so it should be called even if the image wont be used.
    """
    def __init__(
        self,
        images: List['pygame.surface.Surface'],
        animation_velocity: Union[int, float] = 1,
        loop: bool = False
    ):
        """
        Args:
            images (List[pygame.surface.Surface]): List of images for the animator to iterate through.
            animation_velocity (Union[int, float]): Velocity at which to change the current image index. If set to 1;
                images will be changed at each frame, if set to 0.5; images will be changed every second frame, ...
                Defaults to 1.
            loop (bool): If the animation should loop, can later be set using the set_animation method. Defaults to
                False.
        """
        self.images: List[pygame.surface.Surface] = images
        self.number_of_images: int = len(self.images)
        self.animation_velocity: Union[float, int] = animation_velocity
        # Set the check index method. Different function determine when and how to reset the index.
        if loop:
            self.check_index = self._loop
        else:
            self.check_index = self._normal
        # Initial index at 0
        self.current_index: Union[float, int] = 0

    @property
    def index(self):  # Use in list indexing (has to be int)
        return int(self.current_index)

    @property
    def at_end(self):  # If index is at end of list
        return self.index == self.number_of_images - 1

    def _normal(self) -> None:
        """
        Once all images have been returned it stays at the final image.
        """
        self.current_index = min(
            max(0, self.current_index + self.animation_velocity),
            self.number_of_images - 1
        )

    def _loop(self) -> None:
        """
        Once all images have been returned it loops back.
        """
        self.current_index += self.animation_velocity
        if self.index > self.number_of_images - 1:
            self.current_index = 0

    def set_animation(self, animation_type: str) -> None:
        """
        Method sets the current animation type of the object.
        Options:
            normal: Only loops once over the images and stays at the last image.
            loop: Loops indefinitely.

        Args:
            animation_type (str): Animation type between the currently implemented: normal, loop
        """
        if animation_type == "normal":
            self.check_index = self._normal
        elif animation_type == "loop":
            self.check_index = self._loop
        else:  # Todo raise proper error
            print(f"Cannot set animation type to {animation_type}, not implemented.")

    def reset_index(self) -> None:
        """
        Resets the current image index back to 0 (at beginning).
        """
        self.current_index = 0

    def get(self) -> 'pygame.surface.Surface':
        """
        Method returns current image to display, also updates images index so this method should be called in a loop.

        Returns:
            pygame.surface.Surface: Current image in animation loop.
        """
        self.check_index()
        return self.images[self.index]
