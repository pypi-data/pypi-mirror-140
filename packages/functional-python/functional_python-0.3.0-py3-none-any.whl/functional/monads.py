# language=Markdown
"""
Monadic classes `Functor[K,T]` and `Monad[K, T]` -- abstract monadic interfaces for Functors and Monads data types.
"""

from abc import ABC, abstractmethod
from typing import *

T = TypeVar('T')
R = TypeVar('R')
# noinspection PyTypeChecker
K = TypeVar('K', bound='Functor')
class Functor(Generic[K, T], ABC):
    """
    An abstract generic type of `Functor[K, T]`.
    Represents that the implementation of type `K` is generic over `T` and has methods supporting mapping.
    """
    
    __slots__ = tuple()
    
    @abstractmethod
    def map(self: K, f: Callable[[T], R]) -> K:
        """
        Maps the items in the given Monad and wraps result into a new Functor.
        
        Args:
            f: `Callable[[T], R]`. A function of signature `(T) -> R` which is applied to all elements in the current Functor.
        
        Returns:
            `K: Functor[K, R]`. A Functor containing results of application function `f` to the internal data.
        """
        
        raise NotImplementedError
del K

# noinspection PyTypeChecker
K = TypeVar('K', bound='Monad')
class Monad(Generic[K, T], ABC):
    """
    An abstract generic type of `Monad[K, T]`.
    Represents that the implementation of type `K` is generic over `T` and has methods supporting flat mapping.
    """
    
    __slots__ = tuple()
    
    @abstractmethod
    def flat_map(self, f: Callable[[T], K]) -> K:
        """
        Maps the items in the given Monad into a new Monad.
        
        Args:
            f: `Callable[[T], K]`. A function of signature `(T) -> K` where `T` is data type for the current Monad and `K` is the new Monad.
        
        Returns:
            `K: Monad[K, R]`. An aggregated result of application of function `f` to the internal data of the current Monad.
        """
        
        raise NotImplementedError
    
    @property
    @abstractmethod
    def flatten(self) -> T:
        """
        Flattens the current Monad -- transforms a Monad of Monads into a Monad (i.e., List of Lists into List).
        Signature: `Monad[K, Monad[K, T]] -> Monad[K, T]`.
        
        Returns:
            A flattened monad.
            Return value type is the same as the type of the current monad's internal data.
            Return value is an aggregated data of internal data.
        """
        
        raise NotImplementedError
del K

__all__ = \
[
    'Monad',
    'Functor',
]
