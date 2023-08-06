"""
Module containing base classes for pages.
"""

from typing import List, Tuple, Callable

import pygame

from pyggui.gui.event_handler import EventHandler


class Page:
    """
    Main class other pages should inherit from.
    Page object functions similarly to an Item, it can be moved and resized.
    """
    def __init__(self, controller: 'Controller'):
        """
        Args:
            controller (Controller): Main controller object throughout the game.
        """
        self.controller = controller
        self.display = controller.display
        self.items = []
        self.items_positions = []  # Positions relative to the top left corner of page
        self.background_color = (0, 0, 0)
        size = self.display.get_size()
        self.rect = pygame.Rect(0, 0, size[0], size[1])  # Initial position at (0, 0)

        self.event_handlers: List[EventHandler] = []

        self.parent = None  # Used if page is contained in another page

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

    @property
    def display_size(self):
        return self.controller.game.display_size

    def add_event_handler(self, event_handler: EventHandler) -> None:
        """
        Method adds a page-wide EventHandler object. This event handler is not triggered after the page has been
        redirected from i.e. with the redirect_to or go_back methods of Controller.

        Args:
            event_handler (EventHandler): EventHandler object to add.
        """
        self.controller.input.add_event_handler(event_handler)
        self.event_handlers.append(event_handler)

    def add_event_type_handler(self, event_type: int, handler: Callable):
        """
        Method adds a single page-wide event type handler. The handler callable function gets triggered once the
        event_type appears in the main input loop. This event type handler is not triggered after the page has been
        redirected from i.e. with the redirect_to or go_back methods of Controller.

        Args:
            event_type (int): Pygame event type.
            handler (Callable): Callable function to get called once the event type appears in the main input loop.
        """
        # Create an EventHandler object
        event_handler = EventHandler(types=event_type, handlers=handler)
        self.add_event_handler(event_handler)

    def add_item(self, item: any) -> None:
        """
        Method adds item to page. Items position should be set beforehand.

        Args:
            item (any): Item to add to page. Item must have the update and draw methods.
        """
        item.parent = self
        self.items.append(item)
        self.items_positions.append(item.position)

    def update(self) -> None:
        """
        Method updates every item added to page. Once the item is added, page no longer controlls its position but it
        has its original position stored.
        """
        for i, item in enumerate(self.items):
            item.update()

    def draw(self) -> None:
        """
        Method draws every item added to page.
        """
        for item in self.items:
            item.draw()

    def _on_appearance(self) -> None:
        """
        Private method only called by controller.
        Method gets called once the page has been brought up again. Calls the on_appearance method.
        """
        # Re-add all page event handlers to input
        for event_handler in self.event_handlers:
            self.controller.input.add_event_handler(event_handler)
        self.on_appearance()

    def on_appearance(self) -> None:
        """
        Method gets called once the page been has brought up again. Safe for overriding.
        """
        pass

    def _on_exit(self) -> None:
        """
        Private method only called by controller.
        Method gets called once the page has been redirected from. Calls the on_exit method.
        """
        # Remove all page event handlers from input
        self.controller.input.remove_event_handlers(self.event_handlers)
        self.on_exit()

    def on_exit(self) -> None:
        """
        Method gets called once the page has been redirected from. Safe for overriding.
        """
        pass
