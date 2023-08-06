"""
Module containing the input class which updates and handles keyboard / mouse input.
"""

from typing import Callable, List, Tuple, Dict

import pygame

from pyggui.gui.event_handler import EventHandler


def get_key_pressed_dict() -> dict:
    """
    Method returns a dictionary of currently pressed keys (on current frame).
    # TODO: Sort this out, make pretty
    Returns:
        dict: Dictionary containing button states.
    """
    keys_pressed = pygame.key.get_pressed()
    mouse = pygame.mouse.get_pressed()
    return {
        "left": keys_pressed[pygame.K_LEFT],
        "right": keys_pressed[pygame.K_RIGHT],
        "up": keys_pressed[pygame.K_UP],
        "down": keys_pressed[pygame.K_DOWN],
        "enter": keys_pressed[pygame.K_RETURN],
        "space": keys_pressed[pygame.K_SPACE],
        "backspace": keys_pressed[pygame.K_BACKSPACE],
        "mouse": {
            "left": mouse[0],
            "rel": mouse[1],
            "right": mouse[2]
        },
        "a": keys_pressed[pygame.K_a],
        "b": keys_pressed[pygame.K_b],
        "c": keys_pressed[pygame.K_c],
        "d": keys_pressed[pygame.K_d],
        "e": keys_pressed[pygame.K_e],
        "f": keys_pressed[pygame.K_f],
        "g": keys_pressed[pygame.K_g],
        "h": keys_pressed[pygame.K_h],
        "i": keys_pressed[pygame.K_i],
        "j": keys_pressed[pygame.K_j],
        "k": keys_pressed[pygame.K_k],
        "l": keys_pressed[pygame.K_l],
        "m": keys_pressed[pygame.K_m],
        "n": keys_pressed[pygame.K_n],
        "o": keys_pressed[pygame.K_o],
        "p": keys_pressed[pygame.K_p],
        "r": keys_pressed[pygame.K_r],
        "s": keys_pressed[pygame.K_s],
        "t": keys_pressed[pygame.K_t],
        "u": keys_pressed[pygame.K_u],
        "v": keys_pressed[pygame.K_v],
        "z": keys_pressed[pygame.K_z],
        "x": keys_pressed[pygame.K_x],
        "y": keys_pressed[pygame.K_y],
    }


class Input:
    """
    Main class for handling keyboard and mouse input. TODO: Update this mess
    """
    def __init__(self, game: 'Game'):
        """
        Args:
            game (Game): Main game object.
        """
        self.game = game
        # Internal attributes used in the gui
        # Save as two consecutive mouse positions / clicks, accessible through properties
        self.mouse_position: Tuple[int, int] = (0, 0)  # Current mouse position
        self.key_pressed: Dict = {}  # Keys pressed dictionary
        self._mouse_pressed: List[bool, bool] = [False, False]  # Two consecutive mouse clicks, handled in properties
        self.mouse_clicked: bool = False  # Gets set by event, above is set every frame
        self.mouse_movement: Tuple[int, int] = (0, 0)  # Movement of mouse between two consecutive calls
        self.mouse_scroll: int = 0   # Wheel on the mouse, 1 if up -1 if down roll
        # Events
        self.event_types: Dict[str, Callable] = {}
        # Initial update
        self.update()

    @property
    def mouse_pressed(self) -> bool:
        """
        If mouse was clicked on current frame.

        Returns:
            bool: If clicked
        """
        return self._mouse_pressed[-1]  # Last click

    @mouse_pressed.setter
    def mouse_pressed(self, clicked: bool) -> None:
        """
        Mouse pressed on current frame.

        Args:
            clicked (bool): If mouse pressed
        """
        self._mouse_pressed.append(clicked)
        self._mouse_pressed = self._mouse_pressed[-2:]  # Save as only the last 2 recent clicks

    @property
    def previous_mouse_pressed(self) -> bool:
        """
        If mouse was pressed on previous frame.

        Returns:
            bool: If pressed
        """
        return self._mouse_pressed[0]  # Left one is the previous one as we append clicks

    def add_event_handler(self, event_handler: EventHandler) -> None:
        """
        Method adds event handler object to self, its event types are added to the event types dictionary,
        its handlers get triggered once the type appears in the main input loop.

        Args:
            event_handler (EventHandler): EventHandler object to add.
        """
        for event_type in event_handler.types:
            if event_type in self.event_types:
                self.event_types[event_type].append(event_handler)
            else:
                self.event_types[event_type] = [event_handler]

    def add_event_type_handler(self, event_type: int, handler: Callable) -> None:
        """
        Method adds a single event type handler. The handler will get called once the event_type appears in the input
        main loop.

        Args:
            event_type (int): Pygame event type integer number
            handler (Callable): Callable function to get called once the event type appears in the input main loop.
        """
        # Create an EventHandler object
        event_handler = EventHandler(types=event_type, handlers=handler)
        self.add_event_handler(event_handler)

    def remove_event_handler(self, event_handler: EventHandler) -> None:
        """
        Method removes passed EventHandler from self.

        Args:
            event_handler (EventHandler): EventHandler object to remove
        """
        for event_type in event_handler.types:
            if event_type in self.event_types:
                # Create new list object, add only EventHandlers that are not the passed event_handler
                self.event_types[event_type] = [eh for eh in self.event_types[event_type] if not (eh is event_handler)]

    def remove_event_handlers(self, event_handlers: List[EventHandler]) -> None:
        """
        Method removes all passed event handler objects from self.
        EventHandlers therefor wont be triggered anymore.

        Args:
            event_handlers (List[EventHandler]): List of EventHandler objects to remove
        """
        for event_handler in event_handlers:
            self.remove_event_handler(event_handler)

    def __process_event_type_handlers(self, event: 'Event') -> None:
        """
        Method handles events set in event_types, these are added by users (pages and or items).

        Args:
            event (Event): Pygame Event object.
        """
        if event.type in self.event_types:  # Check if handler was added
            for handler in self.event_types[event.type]:
                handler.update(event=event)  # Call EventHandlers update method, pass it the event

    def __process_events(self, event: 'Event') -> None:
        """
        Method handles events used internally by gui items and or controller.
        Updates attributes.

        Args:
            event (Event): Pygame Event object.
        """
        # Mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.mouse_clicked = True
        else:
            self.mouse_clicked = False
        # Mouse wheel event
        if event.type == pygame.MOUSEWHEEL:
            self.mouse_scroll = event.y  # This attribute has to be reset outside this event loop

    def update(self) -> bool:
        """
        Main loop for going over Pygame events.
        Loop goes over user added events.

        Returns:
            bool: False if game was quit, True otherwise
        """
        for event in pygame.event.get():
            # Process user added events first
            self.__process_event_type_handlers(event)
            # Process own events
            self.__process_events(event)
            # Quit event
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
        # Update data used by items and controller
        # We do this at the end as mouse.get_pressed might not work as expected if called before pygame.event.get()
        self.mouse_position = pygame.mouse.get_pos()
        key_pressed = get_key_pressed_dict()
        self.key_pressed = key_pressed
        self.mouse_pressed = key_pressed["mouse"]["left"]
        self.mouse_movement = pygame.mouse.get_rel()  # Movement of mouse on two consecutive calls
        return True
