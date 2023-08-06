# language=Markdown
"""
Utilities Module -- miscellaneous functions and classes used across the package.
"""

from abc import ABC, abstractmethod
from dataclasses import is_dataclass, dataclass
from typing import *

try:
    # noinspection PyProtectedMember
    from dataclasses import _FIELDS
except ImportError:
    _FIELDS = '__dataclass_fields__'

C = TypeVar('C')
def unmake_dataclass(cls: Type[C]) -> Type[C]:
    """
    Unregisters the given class `cls` from being a `dataclass`.
    It keeps all its DataClass properties (including dataclass nesting potential)
    but not its `__dataclass_fields__` which are the only criteria
    `dataclasses.is_dataclass()` decides if the argument is a dataclass.
    
    Actually modifies the existing class object rather than creates a new one.
    In other words, this statement is true: ```unmake_dataclass(cls) is cls```
    
    Args:
        cls: `Type[C]`. Class to be "undataclassed".
    
    Returns:
        `Type[C]`. Returns the same class.
    """
    
    if (not isinstance(cls, type)):
        raise TypeError(f"Dataclass type expected, got {type(cls).__name__!r}: {cls!r}")
    elif (not is_dataclass(cls)):
        raise TypeError("Unable to unmake class that is not a dataclass")
    
    delattr(cls, _FIELDS)
    assert not is_dataclass(cls), f"Assertion failed: {cls.__name__!r}"
    
    # noinspection PyTypeChecker
    return cls


@dataclass(frozen=True)
class PrettyException(Exception, ABC):
    """ Abstract class providing base to all exceptions in the package. """
    
    def __post_init__(self):
        super().__init__(self.message)
    
    @property
    @abstractmethod
    def message(self) -> str:
        """ String representation of the error message """
        raise NotImplementedError


__all__ = \
[
    'unmake_dataclass',
    'PrettyException',
]
