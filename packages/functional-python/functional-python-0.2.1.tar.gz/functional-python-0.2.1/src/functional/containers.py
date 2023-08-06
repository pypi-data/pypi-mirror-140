# language=Markdown
"""
Class `FContainer[T]` -- an abstract container defining abstract mapping, iterative, and other methods.
"""

from abc import ABC, abstractmethod
from typing import *

from .monads import *

T = TypeVar('T')
R = TypeVar('R')
K = TypeVar('K', bound=Monad)
class FContainer(Monad[K, T], Functor[K, T], Generic[K, T], Container[T], ABC):
    """
    Abstract class representing an abstract container holding data of type `T`.
    It is also `Monad` and `Functor` over `T`.
    """
    
    __slots__ = tuple()
    
    empty: K
    """ A special class property containing the empty instance. """
    
    @property
    @abstractmethod
    def is_empty(self) -> bool:
        """ Returns True if the container is empty, False otherwise. """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def non_empty(self) -> bool:
        """ Returns True if the container is non-empty, False otherwise. """
        raise NotImplementedError
    
    @abstractmethod
    def foreach(self, f: Callable[[T], Any]) -> None:
        """
        Apply the given function `f` to all values of the current container.
        The function results is ignored.
        
        This application can be either synchronous or lazy, depending on the implementation.
        
        Args:
            f: `Callable[[T], Any]`. A function of signature `(T) -> ...` that is applied.
        """
        
        raise NotImplementedError


__all__ = \
[
    'FContainer',
]
