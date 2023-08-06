# language=Markdown
"""
Class `Option[T]` -- type-safe replacement for `typing.Optional('T')`.
"""

import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import *

from .containers import *
from .final import final_class
from .monads import *
from .predef import *
from .typing_wrapper import *
from .util import unmake_dataclass, PrettyException

__pdoc__ = dict()

DISABLE_WARNING: bool
""" Module global variable storing if `EmptySomeWarning` should be ignored or not. """

DISABLE_WARNING = False

@dataclass(frozen=True)
class EmptyOption(PrettyException, ValueError):
    """ An exception that is thrown whenever an empty `Option` is attempted to extract its value. """
    
    @property
    def message(self) -> str:
        return "Could not 'get' from an empty Option"

@dataclass(frozen=True)
class EmptySomeWarning(PrettyException, UserWarning):
    """ A warning that is thrown whenever Python's `None` is about to be put into the `Some` class (non-empty `Option`). """
    
    @property
    def message(self) -> str:
        return ' '.join \
        ([
            "'Some' Option with 'None' value detected.",
            "Usually this is an error.",
            "If it is not, you can suppress this warning by setting `functional.option.DISABLE_WARNING = True`.",
        ])

T = TypeVar('T')
R = TypeVar('R')
K = TypeVar('K', bound=Monad)
@unmake_dataclass
@dataclass(frozen=True, init=False, repr=False)
class Option(FContainer['Option[T]', T], Monad['Option[T]', T], Functor['Option[T]', T], Generic[T], ABC):
    """
    Represents optional values.
    Instances of Option are either an instance of `Some` or the object `Option.empty`.
    Options are generics of single type parameter.
    
    Examples:
        Scala-like constructor:
        ```python
        x = Some(4)      # Some(4)
        y = Option.empty # Option.empty
        z = none         # Option.empty
        ```
        
        Python-like constructor:
        ```python
        x = Option(4)    # Some(4)
        y = Option(None) # Option.empty
        ```
    """
    
    __slots__ = tuple()
    
    def __new__(cls, value: Optional[T], *, _ignore_selector: bool = False):
        if (_ignore_selector):
            return super().__new__(cls)
        elif (value is None):
            return OptionNone
        else:
            return Some(value)
    
    @classmethod
    def from_optional(cls: Type['Option[T]'], value: Optional[T]) -> 'Option[T]':
        """
        Constructs a new `Option[T]` from the given `typing.Optional[T]`.
        Returns `Option.empty` if the argument is Python `None`, `Some(arg)` otherwise.
        
        Args:
            value: `Optional[T]`. Either `None` or some value.
        
        Returns:
            `Option[T]`. Either `Option.empty` or `Some(...)`.
        """
        
        return Option(value)
    
    @classmethod
    def is_option(cls: Type['Option[T]'], value: Any) -> bool:
        """
        Class method which checks if the given value is an `Option`.
        Returns `True` if it is.
        
        Args:
            value: A potential `Option` to check.
        
        Returns:
            `bool`
        
        """
        return isinstance(value, Option)
    
    #region Properties
    @property
    def is_defined(self) -> bool:
        """ Returns True if the current Option is non-empty, False otherwise. """
        return not self.is_empty
    
    @property
    def non_empty(self) -> bool:
        """ Returns True if the current Option is non-empty, False otherwise. """
        return self.is_defined
    
    @property
    @abstractmethod
    def get(self) -> T:
        """
        Extracts the internal value of the current Option.
        Raises `EmptyOption` error if the Option is empty.
        
        Returns:
            `T`: Internal Option value. Potentially guarded that it is not `None`.
        """
        raise NotImplementedError
    
    @property
    def flatten(self) -> T:
        """
        Transforms `Option[Option[T]]` into `Option[T]`.
        Returns `Option.empty` if either the current Option, or its internal value is empty,
        and `Some(...)` otherwise.
        
        Returns:
            `Option[T]`: A flattened Option.
        """
        
        return self.flat_map(identity)
    
    @property
    @abstractmethod
    def as_optional(self) -> Optional[T]:
        """
        Transforms current `Option[T]` into Python `typing.Optional[T]`.
        Empty Options are transformed into None, other into the internal data.
        
        Returns:
            `typing.Optional[T]`. Either `None`, or some data.
        """
        
        raise NotImplementedError
    
    @abstractmethod
    def tuple_transform(self, num_items: int) -> Tuple['Option[T]', ...]:
        """
        Transforms an Option of Tuples into a Tuple of Options.
        
        Examples:
            ```python
            Some((1, 2, 3)).tuple_transform(3)  # (Some(1), Some(2), Some(3))
            Option.empty.tuple_transform(3)     # (Option.empty, Option.empty, Option.empty)
            ```
        
        Args:
            num_items: `int`. A number of items in the self-tuple.
                This argument is ignored for non-empty Options.
        
        Returns:
            `Tuple[Option[T], ...]`: A tuple of Options storing the internal data.
        """
        
        raise NotImplementedError
    #endregion
    
    #region Methods
    @abstractmethod
    def get_or_else(self, or_else: T) -> T:
        """
        Getter of the option value with a non-lazy fallback.
        Returns internal value for non-empty Options, and `or_else` otherwise.
        
        If you are interested in the lazy fallback, use `or` operator (see: Option.__bool__).
        
        Args:
            or_else: `T`. A non-lazy fallback.
        
        Returns:
            `T`: Either Option internal value, or the `or_else` argument.
        """
        
        raise NotImplementedError
    
    @abstractmethod
    def flat_map(self, f: Callable[[T], 'Option[R]']) -> 'Option[R]':
        """
        Maps the value of the current Option using the given function `f` into a new Option..
        Empty Options remain empty, non-empty Options may become non-empty.
        
        Unlike many other mapping functions, this is one synchronous (non-lazy).
        
        Args:
            f: `Callable[[T], Option[R]]`. A function of signature `(T) -> Option[R]` that is applied to the non-empty options.
        
        Returns:
            `Option[R]`: Option.empty, or the result of function `f`.
        """
        
        raise NotImplementedError
    
    def map(self, f: Callable[[T], R]) -> 'Option[R]':
        """
        Maps the value of the current Option using the given function `f`.
        Empty Options remain empty, non-empty Options remain non-empty.
        
        Unlike many other mapping functions, this is one synchronous (non-lazy).
        
        Args:
            f: `Callable[[T], R]`. A function of signature `(T) -> R` that is applied to the non-empty options.
        
        Returns:
            `Option[R]`: A new option potentially holding the result of mapping.
        """
        
        return self.flat_map(lambda x: Some(f(x)))
    
    def foreach(self, f: Callable[[T], Any]):
        """
        If the current Option is non-empty, apply function `f` to its internal value.
        Does nothing for empty Options.
        
        Same as `Option.map`, but (a) the mapping is guaranteed to be synchronously happen and (b) the result is ignored.
        
        Args:
            f: `Callable[[T], R]`. A function of signature `(T) -> R` that is applied to the non-empty options.
        """
        
        for v in self: f(v)
    #endregion
    
    #region Operators
    def __bool__(self) -> bool:
        return self.is_defined
    
    def __len__(self) -> int:
        return int(self.is_defined)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    @abstractmethod
    def __contains__(self, item: T) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError
    #endregion

@final
@final_class
@unmake_dataclass
@dataclass(frozen=True, repr=False)
class Some(Option[T], Generic[T]):
    """
    A class representing an instance of non-empty `Option`.
    
    Changes:
        Changed in version 0.2.0: Now throws warnings when `Some(None)` is called.
    """
    
    __slots__ = ('_value', )
    _value: T
    
    def __new__(cls, *args, **kwargs):
        kwargs['_ignore_selector'] = True
        return super().__new__(cls, *args, **kwargs)
    
    def __post_init__(self):
        if (self._value is None and not DISABLE_WARNING):
            warnings.warn(EmptySomeWarning())
    
    #region Properties
    @property
    def is_empty(self):
        return False
    
    @property
    def get(self) -> T:
        return self._value
    
    @property
    def as_optional(self) -> T:
        return self._value
    
    def tuple_transform(self, num_items: int) -> Tuple['Some[T]', ...]:
        return tuple(map(Some, self._value))
    # endregion
    
    # region Methods
    def get_or_else(self, or_else: T) -> T:
        return self._value
    
    def flat_map(self, f: Callable[[T], Option[R]]) -> Option[R]:
        return f(self._value)
    # endregion
    
    # region Operators
    def __repr__(self):
        return f"Some({self._value!r})"
    
    def __contains__(self, item: T) -> bool:
        return self._value == item
    
    def __iter__(self) -> Iterator[T]:
        yield self._value
    # endregion

@final
@final_class
@unmake_dataclass
@dataclass(frozen=True, repr=False, init=False)
class _OptionNone(Option[T], Generic[T]):
    """
    A class representing an instance of an empty `Option`.
    This class SHOULD have only one instance which is stored at `Option.empty`.
    Any other attempts to construct a new instance of this class are illegal.
    """
    
    __slots__ = tuple()
    
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, None, _ignore_selector=True)
    
    # region Properties
    @property
    def is_empty(self):
        return True
    
    @property
    def get(self) -> T:
        raise EmptyOption()
    
    @property
    def as_optional(self) -> None:
        return None
    
    def tuple_transform(self, num_items: int) -> Tuple['_OptionNone[T]', ...]:
        return tuple([ OptionNone ] * num_items)
    # endregion
    
    # region Methods
    def get_or_else(self, or_else: T) -> T:
        return or_else
    
    def flat_map(self, f: Callable[[T], Option[R]]) -> '_OptionNone[R]':
        # noinspection PyTypeChecker
        return none
    # endregion
    
    # region Operators
    def __str__(self):
        return 'None'
    
    def __repr__(self):
        return 'Option.empty'
    
    def __contains__(self, item: T) -> bool:
        return False
    
    def __iter__(self):
        return
        # noinspection PyUnreachableCode
        yield
    # endregion

T1 = TypeVar('T1')
T2 = TypeVar('T2')
T3 = TypeVar('T3')
T4 = TypeVar('T4')
T5 = TypeVar('T5')
T6 = TypeVar('T6')

@overload
def tuple_transform(opt: Option[Tuple[T1]], num_items: int) -> Tuple[Option[T1]]:
    pass
@overload
def tuple_transform(opt: Option[Tuple[T1, T2]], num_items: int) -> Tuple[Option[T1], Option[T2]]:
    pass
@overload
def tuple_transform(opt: Option[Tuple[T1, T2, T3]], num_items: int) -> Tuple[Option[T1], Option[T2], Option[T3]]:
    pass
@overload
def tuple_transform(opt: Option[Tuple[T1, T2, T3, T4]], num_items: int) -> Tuple[Option[T1], Option[T2], Option[T3], Option[T4]]:
    pass
@overload
def tuple_transform(opt: Option[Tuple[T1, T2, T3, T4, T5]], num_items: int) -> Tuple[Option[T1], Option[T2], Option[T3], Option[T4], Option[T5]]:
    pass
@overload
def tuple_transform(opt: Option[Tuple[T1, T2, T3, T4, T5, T6]], num_items: int) -> Tuple[Option[T1], Option[T2], Option[T3], Option[T4], Option[T5], Option[T6]]:
    pass
def tuple_transform(opt: Option[Tuple[T, ...]], num_items: int) -> Tuple[Option[T], ...]:
    """ An alias for `Option.tuple_transform()`. """
    return opt.tuple_transform(num_items)

Option.empty = _OptionNone()
OptionNone = Option.empty
""" An alias for `Option.empty`. """
none = Option.empty
"""
An alias for `Option.empty`.
Pending deprecation since version 0.2.0.
Would be deprecated in version 0.3.0.
"""
is_option = Option.is_option
""" An alias for `Option.is_option`. """

def as_optional(o: Option[T]) -> Optional[T]:
    """
    An alias for `Option.as_optional`.
    
    Transforms given `Option[T]` into Python `typing.Optional[T]`.
    Empty Options are transformed into None, other into the internal data.
    
    Returns:
        `typing.Optional[T]`. Either `None`, or some data.
    """
    return o.as_optional


__all__ = \
[
    'EmptyOption',
    'EmptySomeWarning',
    'Option',
    'Some',
    'OptionNone',
    'none',
    'as_optional',
    'is_option',
    'tuple_transform',
]

__pdoc__['DISABLE_WARNING'] = True
__pdoc__['_OptionNone'] = True
