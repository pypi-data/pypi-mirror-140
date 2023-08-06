# language=Markdown
"""
Predef Module -- predefined simple functions.
"""

from typing import *

T = TypeVar('T')
R = TypeVar('R')
def identity(x: T) -> T:
    """
    Identity Function -- returns its argument unchanged.
    A shorter alias for `lambda x: x`.
    
    Examples:
        Useful for flattening data:
        ```python
        def flatten(monad: Monad[K, Monad[K, T]]) -> Monad[K, T]:
            return monad.flat_map(identity)
        ```
    """
    
    return x

def call(func: Callable[[T], R], *args, **kwargs) -> R:
    """
    Calls the given function `func` with the given `*args` and `**kwargs`.
    A shorter alias for `lambda f, *args, **kwargs: f(*args, **kwargs)`.
    """
    return func(*args, **kwargs)

def star_call(func: Callable[[T], R], args, **kwargs) -> R:
    """
    Calls the given function `func` with the given `*args` and `**kwargs`.
    Applies starring to the `args`.
    A shorter alias for `lambda f, args, **kwargs: f(*args, **kwargs)`.
    """
    return func(*args, **kwargs)

def starmap_call(func: Callable[[T], R], kwargs, **extra_kwargs) -> R:
    """
    Calls the given function `func` with the given `**kwargs`.
    Applies star-mapping to the `kwargs`.
    A shorter alias for `lambda f, kwargs, **extra_kwargs: f(**kwargs, **extra_kwargs)`.
    """
    return func(**kwargs, **extra_kwargs)

__all__ = \
[
    'call',
    'identity',
    'star_call',
    'starmap_call',
]
