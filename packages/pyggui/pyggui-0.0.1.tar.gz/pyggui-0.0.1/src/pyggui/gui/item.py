"""
Module containing Item base classes.
"""

from typing import Callable, List, Tuple, Union

import pygame

from pyggui.helpers.helpers import create_object_repr


class BaseItem:
    """
    Base class for all items.
    """
    def __init__(self, position: List[int], size: Tuple[int, int], visible: bool = True, selected: bool = False):
        self.display = pygame.display.get_surface()

        self.initial_position = position  # Save initial position
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])

        self.items: List[any] = []  # List of items attached to self
        self.items_positions: List[Tuple[int, int]] = []

        self.visible = visible
        self.selected: bool = selected

        self.parent = None  # This points to the item where this one is contained at

    @property
    def position(self) -> List[int]:
        return [self.rect.x, self.rect.y]

    @position.setter
    def position(self, pos: List[int]):
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    @property
    def x(self) -> int:
        return self.rect.x

    @x.setter
    def x(self, new_x: int):
        self.rect.x = new_x

    @property
    def y(self) -> int:
        return self.rect.y

    @y.setter
    def y(self, new_y: int):
        self.rect.y = new_y

    @property
    def size(self) -> Tuple[int, int]:
        return self.rect.size

    @size.setter
    def size(self, new_size: Tuple[int, int]):
        self.rect.size = new_size

    @property
    def width(self) -> int:
        return self.rect.width

    @width.setter
    def width(self, new_width: int) -> None:
        self.rect.width = new_width

    @property
    def height(self) -> int:
        return self.rect.height

    @height.setter
    def height(self, new_height: int) -> None:
        self.rect.height = new_height

    def reset_position(self) -> None:
        """
        Method resets items position to its initial one.
        """
        self.position = self.initial_position

    def update_items_positions(self) -> None:
        """
        Method updates every attached items position relative to self.
        """
        for i, item in enumerate(self.items):
            item.position = [self.x + self.items_positions[i][0], self.y + self.items_positions[i][1]]

    def move(self, change: Union[Tuple[int, int], List[int]]) -> None:
        """
        Method moves item by specified change along with every attached item.

        Args:
            change (Union[Tuple[int, int], List[int]]): dx, dy to move item in each direction.
        """
        self.position = [self.x + change[0], self.y + change[1]]
        self.update_items_positions()

    def move_to(self, point: Union[List[int], Tuple[int, int]]) -> None:
        """
        Method moves item to specified position along with every attached item.

        Args:
            point (Union[List[int], Tuple[int, int]]): x, y point to move item to on screen or page.
        """
        self.position = point
        self.update_items_positions()

    def add_item(self, item: any, relative_position: Union[Tuple[int, int], List[int]] = None) -> None:
        """
        Method adds item to self. If relative position is not specified, item will be added based on its position
        relative to this items position. If relative position is specified however, item will be added into that
        position relative to this items position.

        Args:
            item (any): Item to add to self.
            relative_position (Union[Tuple[int, int], List[int]]): Optional; [x, y] value of added items position
                relative to this items upper left corner.
        """
        if not relative_position:
            relative_position = [item.x - self.x, item.y - self.y]
        item.position = [self.x + relative_position[0], self.y + relative_position[1]]
        item.parent = self  # Point to self as parent
        self.items.append(item)
        self.items_positions.append(relative_position)

    def update(self):
        # Dummy method, some items do not get updated but pages still cal the update method.
        # This should be overwritten.
        pass

    def draw(self):
        # Dummy method, some items do not get drawn but pages still call the draw method.
        # This should be overwritten.
        pass

    def __repr__(self) -> str:
        return create_object_repr(self)


class Item(BaseItem):
    """
    Class for items that are interactive but dependant on controller object.
    Items have hovered property which is set to true once the item is hovered by mouse. Have on_click method to trigger
    an action once the item is clicked.
    """
    def __init__(
        self,
        controller: 'Controller',
        position: List[int] = [0, 0],
        size: Tuple[int, int] = (1, 1),
        on_click: Callable = None,
        movable: bool = False,
        visible: bool = True
    ):
        """
        Args:
            controller (Controller): Main controller object.
            position (List[int] = [0, 0]): Position to place item on screen (or on page).
            size (Tuple[int, int] = (1, 1)): Size of item.
            on_click (Callable): Callable function that gets called once the item is clicked. Default to None.
            movable (bool): If set to true item accepts double error clicks from mouse. (One normal mouse click is
                usually mora than one received click). Defaults to False.
            visible (bool): If item is currently visible.
        """
        super().__init__(position, size, visible)

        self.controller = controller
        self.display = controller.display
        # _on_click is a list of callable functions, where each gets executed once the click event is triggered
        self._on_click: List[Callable] = []
        self.add_on_click(on_click)

        self._last_click_time = 0  # Time of last click
        self.debounce_interval = 150  # Minimum milliseconds passed since last click to accept next click

        # Assign mouse clicked different function, if true -> mouse_clicked() returns true if mouse is pressed
        #                                             else -> mouse_clicked() returns true if mouse clicked
        # Mouse clicked has to be a function so it returns the pointer to the object and not its value
        self.movable = movable
        if self.movable:
            self.debounce_interval = 0
        # Was pressed property used for checking if mouse was pressed on item initially and is still being pressed
        self.was_pressed = False

    @property
    def mouse_clicked(self):
        if self.movable:
            return self.controller.input.mouse_pressed
        else:
            return self.controller.input.mouse_clicked

    def add_on_click(self, on_click: Union[Callable, List[Callable], Tuple[Callable]]) -> None:
        """
        Method adds callable function or list of functions to self. These functions get executed once the item
        is clicked.

        Args:
            on_click (Union[Callable, List[Callable], Tuple[Callable]]): Either a callable function or a list / tuple
            of callable functions.
        """
        if on_click:
            if isinstance(on_click, (list, tuple)):
                self._on_click += [func for func in on_click]
            else:
                self._on_click.append(on_click)

    def debounce_time(self) -> bool:
        """
        Method checks if enough(debounce_interval) time passed from the time of the last click.
        Used for eliminating double clicks.

        Returns:
            bool: If debounce_interval time has passed or not
        """
        return pygame.time.get_ticks() - self._last_click_time >= self.debounce_interval

    def on_click(self):
        """
        Method gets executed once the item has been clicked on.
        Executes all on_click functions.
        """
        # When mouse clicks on item
        self._last_click_time = pygame.time.get_ticks()
        # Trigger functions
        for func in self._on_click:
            func()

    def update(self):
        """
        Used for updating all items attached to it(sizes, positions, etc.).
        """
        self.hovered = self.rect.collidepoint(self.controller.input.mouse_position)
        # Check if mouse was clicked on item, in the interval of the debounce time
        if self.hovered:
            if self.mouse_clicked and self.debounce_time():
                self.on_click()
                self.was_pressed = True
        # Mouse was released
        elif not self.mouse_clicked:
            self.was_pressed = False
        # If was pressed and mouse is not on the item anymore still call on_click method works if movable = True
        if self.was_pressed and self.movable:  # Only check if item is movable, otherwise get multiple clicks
            self.on_click()
        # Update all items
        for item in self.items:
            item.update()

    def draw(self):
        """
        Used for drawing itself and every item attached to it.
        """
        # Logic for drawing itself goes here
        for item in self.items:
            item.draw()

    def __repr__(self) -> str:
        return create_object_repr(self)


class StaticItem(BaseItem):
    """
    Class for static items that are not intractable (can't be clicked and do not have hovered property).
    """
    def __init__(
        self,
        position: List[int] = [0, 0],
        size: Tuple[int, int] = (1, 1),
        visible: bool = True,
        selected: bool = False
    ):
        """
        Args:
            position (List[int] = [0, 0]): Position to place item on screen (or on page).
            size (Tuple[int, int] = (1, 1)): Size of item.
            visible (bool): If item is currently visible.
            selected (bool): If item is currently selected.
        """
        super().__init__(position, size, visible, selected)

    def update(self) -> None:
        """ Used for updating all items attached to it(sizes, positions, etc.). """
        for item in self.items:
            item.update()

    def draw(self) -> None:
        """ Used for drawing itself and every item attached to it. """
        if self.visible:
            for item in self.items:
                item.draw()

    def __repr__(self) -> str:
        return create_object_repr(self)


class ResizableItem(BaseItem):
    """
    Base class for defining static items that have actions performed on them and are able to re-size.
    The main difference between the Item class is that it can be resized, the lack of on_hover / on_click methods
    and that this class does not need the controller to be passed.
    Items can not be attached to this class.
    """
    def __init__(self,
                 position: List[int] = [0, 0],
                 size: Tuple[int, int] = (1, 1),
                 visible: bool = True,
                 selected: bool = False
                 ):
        """
        Args:
            position (List[int]): Position of item.
            size (Tuple[int, int]): Initial size of item.
            visible (bool): If item currently visible. Defaults to True.
            selected (bool): If item currently selected. Defaults to False.
        """
        super().__init__(position, size, visible, selected)

        # These get modified inside this class
        self.initial_size = self.size
        self.is_resized = False
        self.moved_position = [0, 0]
        self.resized_factor = 1

        # These should be modified by the child class
        self.resized_size = self.size
        self.resized = None

    @property
    def scaled_x(self) -> int:
        """
        Property returns scaled x position when item is re-sized, keeping original position intact.
        """
        return self.x + self.moved_position[0]

    @property
    def scaled_y(self) -> int:
        """
        Property returns scaled y position when item is re-sized, keeping original position intact.
        """
        return self.y + self.moved_position[1]

    @property
    def scaled_position(self) -> List[int]:
        """
        Property returns scaled position when item is re-sized, keeping original position intact.
        """
        return [self.scaled_x, self.scaled_y]

    @property
    def scaled_width(self) -> int:
        """
        Property returns objects scaled width. If not resized it is the same as its normal width.
        """
        return self.scaled_size[0]

    @property
    def scaled_height(self) -> int:
        """
        Property returns objects scaled height. If not resized it is the same as its normal height.
        """
        return self.scaled_size[1]

    def resize(self, factor: float) -> None:
        """
        Method will re-size item based on a factor passed as argument. If class gets inherited method should first get
        called with super function.

        Args:
            factor (float): Resize factor, 1 is the same size, 0.5 is half size and 2 is double size
        """
        self.resized_factor = factor
        dx = int((self.width - (self.width * factor)) // 2)
        dy = int((self.height - (self.height * factor)) // 2)
        self.moved_position = [dx, dy]
        self.resized_size = [int(self.width * factor), int(self.height * factor)]
        self.is_resized = True

    def reset_size(self) -> None:
        """
        Method will reset its size to the initial.
        """
        self.moved_position = [0, 0]
        self.is_resized = False

    def __repr__(self) -> str:
        return create_object_repr(self)
