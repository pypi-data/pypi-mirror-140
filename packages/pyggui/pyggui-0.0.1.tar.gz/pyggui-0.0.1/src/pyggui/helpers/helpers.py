"""
Module containing various helper functions that don't belong in specific files or directories.
Functions and or objects should be written in pure Python.
"""

from typing import Callable


def create_callable(func: Callable, *args, **kwargs) -> Callable:
    """
    Function creates a callable function where the called function gets passed as an argument along with its
    args and kwargs.

    Args:
        func (Callable): Function to be called
        *args (any): Args passed to passed function
        **kwargs (any): Kwargs passed to passed function

    Returns:
        Callable: Function that executes passed function when called.
    """
    def callable_func(*caller_args, **caller_kwargs):  # Add caller args, used in handling events passing event kwarg
        return func(*args, *caller_args, **kwargs, **caller_kwargs)
    return callable_func


def check_callable_arguments(func: Callable, *args) -> Callable:
    """
    Function checks that the passed callable func accepts arguments passed through args.

    Args:
        func (): Callable function to perform check on.
        *args (): Arguments passed to check presence in passed function.

    Returns:
        Callable: Passed function check passed, otherwise error gets raised.
    """
    var_names = func.__code__.co_varnames
    for i, arg in enumerate(args):
        if var_names[i] != arg:
            error_msg = f"check_function_arguments: Function {func} " \
                        f"does not have the argument {arg} in the right position."
            raise ValueError(error_msg)
    return func


def create_object_repr(instance: any) -> str:
    """
    Function creates an object representation string by reading its class name and all attributes.
    Formatted: ClassName(attr1=val1, attr2=val2, ... , attrN=valN)

    Args:
        instance (any): Object instance.

    Returns:
        str: Representation of object.
    """
    # Get class name
    class_name = instance.__class__.__name__
    # Get attributes and its values, format into string "attr=value, attr=value, ... "
    attr_str = ", ".join([f"{attribute}={value}" for attribute, value in instance.__dict__.items()])
    return f"{class_name}({attr_str})"
