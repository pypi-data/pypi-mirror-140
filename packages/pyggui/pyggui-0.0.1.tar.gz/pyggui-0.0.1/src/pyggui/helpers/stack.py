"""
Module containing Abstract Data Type Stack implementation.
"""


class Stack:
    """
    Abstract Data Type Stack implementation.
    """
    def __init__(self, initial_data: iter = None):
        """
        Args:
            initial_data (iter): Initial data to add to stack.
        """
        self._data = []
        self._counter = 0
        if initial_data:
            for elt in initial_data:
                self.push(elt)

    def empty(self) -> bool:
        """
        Method checks if stack is empty.

        Returns:
            bool: If empty
        """
        return self._counter == 0

    def push(self, element) -> None:
        """
        Method adds element to the top of stack.

        Args:
            element (any): Element to add.
        """
        self._data.append(element)
        self._counter += 1

    def pop(self) -> None:
        """
        Method removes the top element from the stack.
        """
        if self.empty():
            raise ValueError("pop: The stack is already empty.")
        self._data.pop()
        self._counter -= 1

    def peak(self) -> any:
        """
        Method returns the top element of the stack. Does not change the stack.

        Returns:
            any: Element on top of stack.
        """
        if self.empty():
            raise ValueError("peak: The stack is empty.")
        return self._data[-1]

    def take(self) -> any:
        """
        Method returns the top element from the stack while also removing it.

        Returns:
            any: Element on top of stack.
        """
        if self.empty():
            raise ValueError("Stack.take: The stack is empty.")
        el = self._data[-1]
        self._data.pop()
        self._counter -= 1
        return el

    def __len__(self) -> int:
        return self._counter

    def __iter__(self) -> iter:
        return iter(self._data)

    def __str__(self) -> str:
        bt = "Bottom"
        for elt in self._data:
            bt += " : " + str(elt)
        return bt + " : Top"
