"""
Module containing container classes used for storing and moving grouped items.
"""

from typing import List, Tuple

import pygame

from pyggui.gui.item import ResizableItem, StaticItem
from pyggui.exceptions import NotResizableError


class StaticContainer(StaticItem):
    """
    Container object for holding items inside, items are moved with the container.
    Static container can not be resized but can still be moved.
    """
    def __init__(self,
                 position: List[int] = [0, 0],
                 size: Tuple[int, int] = (100, 100),
                 visible: bool = False,
                 selected: bool = False,
                 resizable: bool = False
                 ):
        super().__init__(position, size, visible, selected)
        """
        Args:
            position (List[int]): Position of container on screen or on Page. Defaults to [0, 0, 0].
            size (Tuple[int, int]): Size of container object. Defaults to white.
            visible (bool): If container boundaries rectangle should be displayed. Defaults to False.
            selected (bool): If the container is currently selected. Defaults to False.
            resizable (bool): If the container is resizable. Defaults to false.
        """

        self.resizable: bool = resizable

        self.items_positions: list[tuple] = []  # List containing attached items positions

    def add_item(self, item: any, relative_position: Tuple[int, int]) -> int:
        """
        Method adds item in a position relative to self upper left corner. Item will be moved along with the
        container object.

        Args:
            item (any): Item to add.
            relative_position (Tuple[int, int]): Position of added item in container based on upper left corner.

        Returns:
            int: Position (index) in items list of added item.
        """
        self.items.append(item)
        item_position = [relative_position[0], relative_position[1]]
        self.items_positions.append(item_position)
        self.items[-1].position = item_position  # Update new items position
        return len(self.items) - 1

    def change_item_at_index(self, index: int, item: any) -> None:
        """
        Method changes item at index inside the items list. Position of item inside container stays the same.

        Args:
            index (int): Index in items list to change item.
            item (any): Item to add.
        """
        self.items[index] = item
        self.items[index].position = self.items_positions[index]

    def update(self) -> None:
        """
        Updates all items and its positions relative to self.
        """
        for i, item in enumerate(self.items):
            # Update items positions relative to current self position
            item.position = [self.x + self.items_positions[i][0],
                             self.y + self.items_positions[i][1]]
            item.selected = self.selected
            item.update()

    def draw(self) -> None:
        """
        Used for drawing itself and every item attached to it.
        """
        if self.visible:
            pygame.draw.rect(
                self.display,
                (255, 255, 255),
                self.rect,
                width=1
                )
        for item in self.items:
            item.draw()


class ResizableContainer(ResizableItem):
    """
    Container object can be resized along with every item contained in it. Because of this only re-sizable items can
    be added.
    """
    def __init__(self,
                 position: List[int] = [0, 0],
                 size: Tuple[int, int] = (100, 100),
                 visible: bool = False,
                 selected: bool = False,
                 resizable: bool = False
                 ):
        """
        Args:
            position (List[int]): Position of container on screen or on Page. Defaults to [0, 0, 0].
            size (Tuple[int, int]): Size of container object. Defaults to white.
            visible (bool): If container boundaries rectangle should be displayed. Defaults to False.
            selected (bool): If the container is currently selected. Defaults to False.
            resizable (bool): If the container is resizable. Defaults to false.
        """
        super().__init__(position, size, visible, selected)

        self.resizable: bool = resizable

        self.items_positions: list[tuple] = []  # List containing attached items positions
        self.resized_items_positions: list[tuple] = []

    def resize(self, factor: float) -> None:
        """
        Method re-sizes self and every item inside by a factor passed as an argument.

        Args:
            factor (float): Representing scale to resize in the interval (0, inf]
        """
        super(ResizableContainer, self).resize(factor)
        self.resized_size = [int(self.width * factor), int(self.height * factor)]
        for i, item in enumerate(self.items):  # Re-size and scale items positions based on factor
            self.resized_items_positions[i] = [int(self.items_positions[i][0] * factor),
                                               int(self.items_positions[i][1] * factor)]
            item.resize(factor)

    def reset_size(self) -> None:
        """
        Method resets size of self and every item to the initially set size.
        """
        super(ResizableContainer, self).reset_size()
        self.size = self.initial_size  # Reset size of self rect
        for item in self.items:
            item.reset_size()

    def add_item(self, item: any, relative_position: Tuple[int, int]) -> int:
        """
        Method adds item in a position relative to self upper left corner. Item will be moved along with the
        container object.

        Args:
            item (any): Item to add.
            relative_position (Tuple[int, int]): Position of added item in container based on upper left corner.

        Returns:
            int: Position (index) in items list of added item.
        """
        if self.resizable and not hasattr(item, "is_resized"):  # If container resizable, expect only resizable items
            raise NotResizableError("Added item is not resizable; "
                                    "Container is set to be resizable and only accepts resizable items.")
        self.items.append(item)
        item_position = [relative_position[0], relative_position[1]]
        self.items_positions.append(item_position)
        self.resized_items_positions.append(item_position)
        self.items[-1].position = item_position  # Update this items position
        return len(self.items) - 1

    def change_item_at_index(self, index: int, item: any) -> None:
        """
        Method changes item at index inside the items list. Position of item inside container stays the same.

        Args:
            index (int): Index in items list to change item.
            item (any): Item to add.
        """
        self.items[index] = item
        self.items[index].position = self.items_positions[index]

    def update(self) -> None:
        """
        Updates all items and its positions relative to self.
        """
        for i, item in enumerate(self.items):
            # Update items positions relative to current self position
            item.position = [self.scaled_x + self.resized_items_positions[i][0],
                             self.scaled_y + self.resized_items_positions[i][1]]
            item.selected = self.selected
            item.update()

    def draw(self) -> None:
        """
        Used for drawing itself and every item attached to it.
        """
        if self.visible:
            if self.is_resized:
                pygame.draw.rect(
                    self.display,
                    (255, 255, 255),
                    [self.scaled_x, self.scaled_y, self.resized_size[0], self.resized_size[1]],
                    width=1
                )
            else:
                pygame.draw.rect(
                    self.display,
                    (255, 255, 255),
                    self.rect,
                    width=1
                )
        for item in self.items:
            item.draw()


class Container:
    """
    Container objects can store items in positions relative to self. If items get added to a container object, those
    items can all be moved together by moving the container object.

    Passing the argument resizable as True will create a Resizable container, otherwise a StaticContainer where it and
    its items can't be resized.
    """
    def __new__(cls, *args, **kwargs):
        kwargs_copy = kwargs.copy()  # Mutate copy so all kwargs go through
        resizable = kwargs_copy.pop("resizable", False)
        # Return correct container
        if resizable:
            return ResizableContainer(*args, **kwargs)
        else:
            return StaticContainer(*args, **kwargs)

    def __init__(self,
                 position: List[int] = [0, 0],
                 size: Tuple[int, int] = (100, 100),
                 visible: bool = False,
                 selected: bool = False,
                 resizable: bool = False
                 ):
        """
        Args:
            position (List[int]): Position of container on screen or on Page. Defaults to [0, 0, 0].
            size (Tuple[int, int]): Size of container object. Defaults to white.
            visible (bool): If container boundaries rectangle should be displayed. Defaults to False.
            selected (bool): If the container is currently selected. Defaults to False.
            resizable (bool): If the container is resizable. Defaults to false.
        """
        pass
