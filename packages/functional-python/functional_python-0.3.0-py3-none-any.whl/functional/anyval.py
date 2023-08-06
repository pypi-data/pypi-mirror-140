# language=Markdown
"""
Class `AnyVal[T]` -- type-safe replacement for `typing.NewType('T')`.
"""

from abc import ABC
from typing import *

try:
    from dataclasses_json import global_config as DCJ_GLOBAL_CONFIG
    from dataclasses_json.core import Json
except ImportError:
    DCJ_SUPPORT_ENABLED = False
    DCJ_GLOBAL_CONFIG: Dict[type, Callable] = dict()
    Json = Union[dict, list, str, int, float, bool, None]
else:
    DCJ_SUPPORT_ENABLED = True

from .final import final_class
from .typing_wrapper import *

T = TypeVar('T')
C = TypeVar('C')

class AnyVal(ABC, Generic[T]):
    """
    Helper abstract class to make Scala-like AnyVal's.
    AnyVal is a dataclass-like class with the only field `value`,
    constructor, hash, representation, and equals, as well as encode/decode methods.
    
    If package `dataclasses_json` is installed,
    AnyVal subclasses are registered to have simple decoders and encoders.
    AnyVal subclasses are made to be final.
    
    Generally, works similar to `typing.NewType`, but the field `value` MUST be accepted explicitly.
    
    See Also:
        `functional.final.final_class`
    """
    
    __slots__ = ('value', )
    
    value: Final[T]
    """ An internal value of the `AnyVal` class """
    
    # region Constructors
    def __init__(self, value: T):
        self.value = value
    
    def __init_subclass__(cls, **kwargs):
        if (DCJ_SUPPORT_ENABLED):
            DCJ_GLOBAL_CONFIG.decoders[cls] = cls._decode
            DCJ_GLOBAL_CONFIG.encoders[cls] = cls._encode
        
        super().__init_subclass__(**kwargs)
        final_class(cls)
    # endregion
    
    # region Data Model Functions
    def __hash__(self):
        return hash(self.value)
    
    def __eq__(self, other):
        if (isinstance(other, AnyVal)):
            return type(self) == type(other) and self.value == other.value
        return False
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.value!r})'
    # endregion
    
    # region JSON Coders
    @classmethod
    def decode_value(cls, data: Json) -> T:
        """ Decode data of JSON-accepted type (like dict, str, etc...) and parse internal value from it. """
        return data
    def encode_value(self) -> Json:
        """ Encode internal value to the JSON-accepted type (like dict, str, etc...). """
        return self.value
    
    @classmethod
    def _decode(cls, data):
        return cls(cls.decode_value(data))
    def _encode(self):
        return self.encode_value()
    # endregion


__all__ = \
[
    'AnyVal',
]
