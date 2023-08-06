# language=Markdown
"""
Decorations for Final classes.
Final classes are guarded from being inherited.

```python
from functional.final import final_class

@final_class
class MyFinalClass:
    def __init__(self, x):
        self.x = x

# The following would raise FinalInheritanceError
class ChildClass(MyFinalClass):
    def __init__(self, x = 5):
        super().__init__(x)
```

This is implemented by changing their
`__init_subclass__` method with the one throwing error.
However, any parent `__init_sublass__` are safe:

```python
from functional.final import final_class

class A:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.x = 4

@final_class
class B(A):
    pass

print(B.x) # Prints 4
```

"""

import sys
import warnings
from dataclasses import dataclass
from typing import *

from .typing_wrapper import *
from .util import PrettyException

C = TypeVar('C')

@dataclass(frozen=True)
class FinalInheritanceError(PrettyException, TypeError, Generic[C]):
    """ An exception that is thrown whenever final class is to be inherited from """
    
    cls: Type[C]
    """ A final class being inherited from """
    
    @property
    def message(self) -> str:
        return f"Cannot inherit from final class {self.cls.__qualname__!r}."

@dataclass(frozen=True)
class GenericFinalWarning(PrettyException, RuntimeWarning, Generic[C]):
    """ A warning that is thrown whenever generic final class is to be constructed on older versions of Python """
    
    cls: Type[C]
    """ A final class being constructed """
    
    @property
    def message(self) -> str:
        return f"Class {self.cls.__qualname__!r}: Attempting to construct generic final type. It could work not properly on Python {sys.version_info.major}.{sys.version_info.minor}.x"

@dataclass(frozen=True)
class FinalInheritanceWarning(RuntimeWarning, Generic[C]):
    """ A warning that is thrown whenever generic final class is to be inherited from on older versions of Python """
    
    cls: Type[C]
    """ A final class being inherited from """
    
    def __post_init__(self):
        super().__init__(self.message)
    
    @property
    def message(self) -> str:
        """ String representation of the error message """
        return f"Class {self.cls.__qualname__!r}: Attempting to inherit from generic final class. However, on Python {sys.version_info.major}.{sys.version_info.minor}.x this could not be handled"

def __init_subclass_exception__(cls, **kwargs):
    raise FinalInheritanceError(cls)

def __init_subclass_warning__(cls, **kwargs):
    warnings.warn(FinalInheritanceWarning(cls))

def final_class(cls: Type[C]) -> Type[C]:
    """
    A Decoration which makes the given class `cls` final.
    When inherited, the `FinalInheritanceError` will be raised.
    Also wraps it with `typing.final` decoration if exists, but some IDEs ignore it.
    
    Does not work properly for `typing.Generic` classes in Python 3.6.
    (Works fine for non-generic classes and/or on newer Pythons)
    
    Args:
        cls: A class to be made final.

    Returns:
        Returns the same class.
    
    Changes:
        Changed in version 0.1.2: Now throws warnings when used for Generic classes in Python 3.6
    """
    
    if (sys.version_info < (3, 7)):
        from typing_inspect import is_generic_type
        if (is_generic_type(cls)):
            cls_module, _, _ = getattr(cls, '__module__', '__main__').partition('.')
            this_module, _, _ = __name__.partition('.')
            if (this_module != cls_module):
                warnings.warn(GenericFinalWarning(cls))
            setattr(cls, '__init_subclass_warning__', classmethod(__init_subclass_warning__))
            cls.__init_subclass__ = cls.__init_subclass_warning__
            return final(cls)
    
    setattr(cls, '__init_subclass_exception__', classmethod(__init_subclass_exception__))
    cls.__init_subclass__ = cls.__init_subclass_exception__
    return final(cls)


__all__ = \
[
    # Own implementations
    'FinalInheritanceError',
    'FinalInheritanceWarning',
    'GenericFinalWarning',
    'final_class',
]
