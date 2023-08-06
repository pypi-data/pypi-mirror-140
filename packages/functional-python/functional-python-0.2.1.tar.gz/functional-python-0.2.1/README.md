# Functional Python - Scala-like monadic data types

**Functional Python** is a framework which implements Scala-like monadic data types,
such as [Option] or [Map].

Also implements final class decoration and [AnyVal].

## Why?
##### Method chaining
```python
# ToDo: Example
```

##### Type Safety
```python
# ToDo: Example
```

## Api Description
### Options
Represents optional values.
Instances of Option are either an instance of `Some` or the object `Option.empty`.
Options are generics of single type parameter.

##### Creating an Option
```python
from functional.option import *

# Scala-like constructor
x = Some(4)      # Some(4)
y = Option.empty # Option.empty
z = none         # Option.empty

# Python-like constructor
x = Option(4)    # Some(4)
y = Option(None) # Option.empty
```

Note that `None` which is printed **is not** Python `None`
but is special object which does not contain any value and equals to `Option(None)`:

```python
from functional.option import *

print(str(Option.empty))     # "None"
print(repr(Option.empty))    # "Option.empty"
print(Option.empty is none)  # True
print(Option.empty is None)  # False
```

##### Getting value of an Option
Options implement `.get` property and `.getOrElse(default)` method.
First one checks Option is not empty and either returns value or throws an exception.
Second one returns *default* instead of throwing an exception.

```python
from functional.option import *
x = Some(4)      # Some(4)
y = none         # None

x.get            # 4
y.get            # raises EmptyOption

x.get_or_else(5) # 4
y.get_or_else(5) # 5

# .is_defined returns True if Option is not None
x.is_defined     # True
y.is_defined     # False

# .is_empty is the opposite
x.is_empty       # False
y.is_empty       # True

# .non_empty is the same as .is_defined
x.non_empty      # True
y.non_empty      # False
```

Note that unlike in Scala, this Option's `.get_or_else` is not lazy-evaluated,
so this code will fail:
```python
Some(4).get_or_else(1/0)
```

To prevent, it is recommended use python-like accessors (see below).

##### Mapping an Option
Options are both functors and monads, meaning they possess `.map()` and `.flat_map()` methods
with the following signatures (where object is a type `Option[A]`):
 - `.map(f: A => B): Option[B]` - map value inside an Option.
 - `.flat_map(f: A => Option[B]): Option[B]` - map value inside an Option to an Option.

Both these methods work only on non-empty options, returning `Option.empty` for otherwise.

```python
from functional.option import *
x = Some(4)            # Some(4)
y = none               # None
z = Some(6)            # Some(6)

x.map(lambda v: v + 2) # Some(6)
y.map(lambda v: v + 2) # None
z.map(lambda v: v + 2) # Some(8)

x.flat_map(lambda v: Some(v) if v < 5 else none) # Some(4)
y.flat_map(lambda v: Some(v) if v < 5 else none) # None
z.flat_map(lambda v: Some(v) if v < 5 else none) # None
```

##### Flattening an Option
Sometimes you get an Option which contains Option.
There is special property `.flatten` which converts `Option[Option[T]]` into `Option[T]`

```python
# ToDo: Example
```

##### Python-style accessors
Options support python-like accessors / converters `__bool__`, `__iter__`, `__len__`, and `__enter__/__exit`.

```python
# ToDo: Example
```

### Final Classes
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

### AnyVal
AnyVal is a helper abstract class to make Scala-like [AnyVal]'s.
It is a dataclass-like class with the only field `value`,
constructor, hash, representation, and equals, as well as encode/decode methods.

AnyVal subclasses are made to be final.
Field value is supposed to be write-protected.

Generally, works similar to `typing.NewType`, but the field `value` MUST be accepted explicitly.

```python
from functional.anyval import AnyVal
class CustomID(AnyVal[str]): pass
class OtherAnyVal(AnyVal[str]): pass

custom_id = CustomID('1tt3s')
print(custom_id == '1tt3s')              # False
print(custom_id.value == '1tt3s')        # True
print(custom_id == OtherAnyVal('1tt3s')) # False
```

If package [dataclasses-json] is installed,
AnyVal subclasses are registered to have simple decoders and encoders.
If the data type could not be handled by JSON or DataClassesJSON library,
you can override methods `decode_value` and `encode_value`

```python
from datetime import date
from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass

from functional.anyval import AnyVal

class MyID(AnyVal[int]): pass
class Date(AnyVal[date]):
    @classmethod
    def decode_value(cls, data: str) -> date:
        if (not isinstance(data, str)):
            raise TypeError(f"Cannot decode {date.__name__!r} from type {type(data).__qualname__!r}, ISO-format string required")
        
        return date.fromisoformat(data)
    
    def encode_value(self) -> str:
        return self.value.isoformat()

@dataclass
class Person(DataClassJsonMixin):
    id: MyID
    name: str
    born: Date

peter = Person(MyID(15), name='peter', born=Date(date(1995, 7, 25)))
mark = Person(MyID(-131239231231), name='mark', born=Date(date.fromisoformat('2002-06-15')))

print(peter.to_json()) # {"id": 15, "name": "peter", "born": "1990-01-12"}
print(mark.to_json())  # {"id": -131239231231, "name": "mark", "born": "2002-06-15"}

print(Person.from_json('''{ "name": "Dave", "born": "2021-07-05", "id": 61123236 }'''))
# Person(id=MyID(61123236), name='Dave', born=datetime.date(2021, 7, 5))
```


### Map
**TODO**

## Plans
 - Test coverage
 - Support Maps (both mutable and immutable)
 - Support Lists (both mutable and immutable)


<!-- Links -->
[anyval]: https://docs.scala-lang.org/overviews/scala/AnyVal.html
[map]: https://docs.scala-lang.org/overviews/collections/maps.html
[option]: https://scala-lang.org/api/2.13.x/scala/Option.html
[dataclasses-json]: https://pypi.org/project/dataclasses-json
