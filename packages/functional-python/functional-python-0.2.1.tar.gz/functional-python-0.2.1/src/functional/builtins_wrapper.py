# language=Markdown
"""
Builtins Wrapper -- typed overloads for the Python builtins methods.

## Builtins Wrapper

This module provides typed overloads for some Python builtins methods.
It contains no actual members -- all of them are shadowy wrapped to their builtins implementations.
"""

import builtins
from typing import *

T = TypeVar('T')
R = TypeVar('R')
def shadow_wrapper(other_func: Callable):
    """ Decoration for shadowy replace one function with the other """
    
    def wrapper(_: Callable):
        return other_func
    return wrapper

# noinspection PyShadowingBuiltins
@overload
def map(func: Callable[[T], R], coll: Iterable[T]) -> Iterator[R]:
    pass
# noinspection PyShadowingBuiltins
@shadow_wrapper(builtins.map)
def map(*args, **kwargs):
    return builtins.map(*args, **kwargs)


# noinspection PyShadowingBuiltins
@overload
def sum(iterable: Iterable[T]) -> T:
    pass
# noinspection PyShadowingBuiltins
@overload
def sum(iterable: Iterable[T], start: T) -> T:
    pass
# noinspection PyShadowingBuiltins
@shadow_wrapper(builtins.sum)
def sum(*args, **kwargs):
    return builtins.sum(*args, **kwargs)


__all__ = \
[
    'map',
    'sum',
]
