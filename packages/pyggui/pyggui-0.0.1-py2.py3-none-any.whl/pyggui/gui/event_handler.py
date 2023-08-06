"""
Module containing event handler classes.
"""

from typing import Union, List, Callable


class EventHandler:
    """
    Class stores event types and handlers for those events.
    Once one of the event types appears in the input event loop all of its handlers get called.
    Event types are Pygame specific event types.
    """
    def __init__(self, types: Union[int, List[int]], handlers: Union[Callable, List[Callable]]):
        """
        Args:
            types (Union[int, List[int]]): Event type or list of event types that trigger all handlers
            handlers (Union[Callable, List[Callable]]): Callable function or list of callable functions that get
                triggered once one of the event types appeared in the input event handling loop.
        """
        if isinstance(types, (list, tuple)):
            self._types = [type_ for type_ in types]
        else:
            self._types = [types]
        if isinstance(handlers, (list, tuple)):
            self._handlers = [handler for handler in handlers]
        else:
            self._handlers = [handlers]

    @property
    def types(self):
        return self._types

    @property
    def handlers(self):
        return self._handlers

    def update(self, event: 'Event') -> None:
        """
        Method calls all handlers set to self. Is called once on of the set event types appeared in input.

        Args:
            event (Event): Pygame Event object
        """
        for handler in self._handlers:
            handler(event=event)
