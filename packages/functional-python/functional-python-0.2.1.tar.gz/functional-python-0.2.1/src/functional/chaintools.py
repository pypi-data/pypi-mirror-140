# language=Markdown
"""
ChainTools module -- operations for method chaining and iterables mapping.

## ChainTools Module

This module provides functions for prettier method chaining.
Most of them are implemented by using `functools.reduce()` function.

### Provides:
#### Functions for iterating:
 * `chunks()`
 
#### Functions for mapping and applying:
 * `map_items()`
 * `apply()`
 * `apply_items()`
 
#### Functions with inversed arguments order:
 * `invcall()`
 * `invmap()`
 * `invmap_items()`
 
#### Functions for chaining:
 * `chain()`
 * `chain_map()`
 * `chain_map_items()`

Chain functions also provide typing overloads for up to 6 functions for the better type hinting.
"""

from functools import reduce, partial
from itertools import islice
from typing import *

from .predef import *

T  = TypeVar('T')
T2 = TypeVar('T2')
T3 = TypeVar('T3')
T4 = TypeVar('T4')
T5 = TypeVar('T5')
T6 = TypeVar('T6')
R  = TypeVar('R')


def chunks(coll: Iterable[T], chunk_size: int) -> Iterator[List[T]]:
    """
    Splits an iterable into chunks of given size.
    We have no idea why this method is not part of `itertools` Python module.
    
    Internally implemented using `itertools.slice()`.
    
    Examples:
        ```python
        c = chunks(range(15), 6)
        print(list(c))
        # [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [12, 13, 14]]
        ```
    
    Args:
        coll: `Iterable[T]`. An iterable to be split.
        chunk_size: `int`. A size of all but last chunks in the result. Last chunk could contain fewer number of elements.
    
    Returns:
        `Iterator[List[T]]`.
        Returns an iterator of lists made from the original iterable.
    """
    
    it = iter(coll)
    while True:
        head = list(islice(it, chunk_size))
        if (not head): break
        yield head

def map_items(func: Callable[[T], R], coll: Iterable[Iterable[T]]) -> Iterator[Iterator[R]]:
    """
    Lazy apply function `func` to all elements of the given iterable of iterables `coll`.
    *(Apply function for each element of each iterable from the given iterable.)*
    
    This function do not actuallyy iterate over the original iterable.
    To do so, use `functional.chaintools.apply()` and `functional.chaintools.apply_items()`.
    
    Examples:
        ```python
        c = chunks(range(10), 3)         # Something like: [ [0,1,2], [3,4,5], [6,7,8], [9] ]
        m = map_items(lambda x: x*x, c)  # Transform numbers into their squares
        print(list(map(list, m)))        # Simple print(list(m)) won't work here
        # [[0, 1, 4], [9, 16, 25], [36, 49, 64], [81]]
        ```
    
    Args:
        func: `Callable[[T], R]`. A function of signature `(T) -> R` to be applied for all elements within iterable of iterables.
        coll: `Iterable[Iterable[T]]`. Iterable of iterables which is going to be mapped.
    
    Returns:
        `Iterator[Iterator[R]]`. Returns an iterator of iterators of mapped elements.
    """
    
    return map(partial(map, func), coll)

def apply(func: Callable[[T], Any], coll: Iterable[T]):
    """
    General forEach method.
    Synchronously apply the given function `func` to all elements of iterable `coll`.
    Function results are ignored.
    
    Logically same as ```list(map(func, coll))```, but looks prettier.
    
    Args:
        func: `Callable[[T], Any]`. A function of signature `(T) -> R` to be applied for all elements within iterable.
        coll: `Iterable[T]`. Iterable which is going to be iterated.
    """
    
    for el in coll: func(el)

def apply_items(func: Callable[[T], Any], coll: Iterable[Iterable[T]]):
    """
    General forEachItem method.
    Synchronously apply the given function `func` to all elements of iterable of iterables `coll`.
    Function results are ignored.
    
    Logically same as ```list(map(list, map_items(func, coll)))```, but looks prettier.
    
    Examples:
        ```python
        c = chunks(range(10), 3)         # Chunks of size 3 of numbers from 0 to 9
        m = map_items(lambda x: x*x, c)  # Their squares
        apply_items(print, m)            # Print all these numbers one at a time
        ```
    
    Args:
        func: `Callable[[T], R]`. A function of signature `(T) -> R` to be applied for all elements within iterable of iterables.
        coll: `Iterable[Iterable[T]]`. Iterable of iterables which is going to be applied.
    """
    
    for it in coll:
        for el in it: func(el)

def invcall(func: Callable[[T], R], *args, **kwargs) -> R:
    """ Version of `functional.predef.call()` with inversed arguments order. """
    return call(*reversed(args), func, **kwargs)
def invmap(coll: Iterable[T], func: Callable[[T], R]) -> Iterator[R]:
    """ Version of `builtins.map()` with inversed arguments order. """
    return map(func, coll)
def invmap_items(coll: Iterable[Iterable[T]], func: Callable[[T], R]) -> Iterator[Iterator[R]]:
    """ Version of `functional.chaintools.map_items()` with inversed arguments order. """
    return map_items(func, coll)

@overload
def chain(el: T, func1: Callable[[T], R]) -> R:
    pass
@overload
def chain(el: T, func1: Callable[[T], T2], func2: Callable[[T2], R]) -> R:
    pass
@overload
def chain(el: T, func1: Callable[[T], T2], func2: Callable[[T2], T3], func3: Callable[[T3], R]) -> R:
    pass
@overload
def chain(el: T, func1: Callable[[T], T2], func2: Callable[[T2], T3], func3: Callable[[T3], T4], func4: Callable[[T4], R]) -> R:
    pass
@overload
def chain(el: T, func1: Callable[[T], T2], func2: Callable[[T2], T3], func3: Callable[[T3], T4], func4: Callable[[T4], T5], func5: Callable[[T5], R]) -> R:
    pass
@overload
def chain(el: T, func1: Callable[[T], T2], func2: Callable[[T2], T3], func3: Callable[[T3], T4], func4: Callable[[T4], T5], func5: Callable[[T5], T6], func6: Callable[[T6], R]) -> R:
    pass
def chain(el: T, *funcs: Callable[[T], R]) -> R:
    """
    Chain methods mapping for the given element.
    Just looks prettier than `func5(func4(func3(func2(func1(el)))))`.
    
    Examples:
        Calculate len of hex representation of the given number inputted as string:
        ```python
        chain('1234', int, hex, len) - 2
        # '1234' => 1234 => '0x4d2' => 5 => 3
        # Is the same as:
        len(hex(int('1234'))) - 2
        ```
    
    Args:
        el: A starting element for the sequence of maps.
        *funcs: Any number of functions to be chained. Left-most functions are applied first.
    
    Returns:
        Returns the result of the last function application.
    """
    
    # noinspection PyTypeChecker
    return reduce(invcall, funcs, el)

@overload
def chain_map(coll: Iterable[T], func1: Callable[[T], R]) -> Iterator[R]:
    pass
@overload
def chain_map(coll: Iterable[T], func1: Callable[[T], T2], func2: Callable[[T2], R]) -> Iterator[R]:
    pass
@overload
def chain_map(coll: Iterable[T], func1: Callable[[T], T2], func2: Callable[[T2], T3], func3: Callable[[T3], R]) -> Iterator[R]:
    pass
@overload
def chain_map(coll: Iterable[T], func1: Callable[[T], T2], func2: Callable[[T2], T3], func3: Callable[[T3], T4], func4: Callable[[T4], R]) -> Iterator[R]:
    pass
@overload
def chain_map(coll: Iterable[T], func1: Callable[[T], T2], func2: Callable[[T2], T3], func3: Callable[[T3], T4], func4: Callable[[T4], T5], func5: Callable[[T5], R]) -> Iterator[R]:
    pass
@overload
def chain_map(coll: Iterable[T], func1: Callable[[T], T2], func2: Callable[[T2], T3], func3: Callable[[T3], T4], func4: Callable[[T4], T5], func5: Callable[[T5], T6], func6: Callable[[T6], R]) -> Iterator[R]:
    pass
@overload
def chain_map(coll: Iterable[T], *funcs: List[Callable[[T2], R]]) -> Iterator[R]:
    pass
def chain_map(coll: Iterable[T], *funcs: Callable[[T2], R]) -> Iterator[R]:
    """
    Chain methods mapping for the given iterable.
    Just looks prettier than `map(lambda el: func5(func4(func3(func2(func1(el))))), coll)`
    or even evil devil `map(func5, map(func4, map(func3, map(func2, map(func1, el)))))`.
    
    Examples:
        Calculate len of hex representation of the given list of numbers inputted as string:
        ```python
        numbers = [ '123', '1234', '7', '18123' ]
        chain_map(numbers, int, hex, len, lambda l: l - 2)
        # '123'   => 123   => '0x7b'   => 4 => 2
        # '1234'  => 1234  => '0x4d2'  => 5 => 3
        # '7'     => 7     => '0x7'    => 3 => 1
        # '18123' => 18123 => '0x46cb' => 6 => 4
        # Result: [ 2, 3, 1, 4 ]
        
        # Is the same as:
        map(lambda x: len(hex(int(x))) - 2, numbers)
        map(lambda l: l - 2, map(len, map(hex, map(int, numbers))))
        ```
    
    Args:
        coll: `Iterable[T]`. A starting iterable for the sequence of maps.
        *funcs: Any number of functions to be chained. Left-most functions are applied first.
    
    Returns:
        Returns an iterable containing the results of the last function application.
    """
    
    # noinspection PyTypeChecker
    return reduce(invmap, funcs, coll)


@overload
def chain_map_items(coll: Iterable[Iterable[T]], func1: Callable[[T], R]) -> Iterator[Iterator[R]]:
    pass
@overload
def chain_map_items(coll: Iterable[Iterable[T]], func1: Callable[[T], T2], func2: Callable[[T2], R]) -> Iterator[Iterator[R]]:
    pass
@overload
def chain_map_items(coll: Iterable[Iterable[T]], func1: Callable[[T], T2], func2: Callable[[T2], T3], func3: Callable[[T3], R]) -> Iterator[Iterator[R]]:
    pass
@overload
def chain_map_items(coll: Iterable[Iterable[T]], func1: Callable[[T], T2], func2: Callable[[T2], T3], func3: Callable[[T3], T4], func4: Callable[[T4], R]) -> Iterator[Iterator[R]]:
    pass
@overload
def chain_map_items(coll: Iterable[Iterable[T]], func1: Callable[[T], T2], func2: Callable[[T2], T3], func3: Callable[[T3], T4], func4: Callable[[T4], T5], func5: Callable[[T5], R]) -> Iterator[Iterator[R]]:
    pass
@overload
def chain_map_items(coll: Iterable[Iterable[T]], func1: Callable[[T], T2], func2: Callable[[T2], T3], func3: Callable[[T3], T4], func4: Callable[[T4], T5], func5: Callable[[T5], T6], func6: Callable[[T6], R]) -> Iterator[Iterator[R]]:
    pass
@overload
def chain_map_items(coll: Iterable[Iterable[T]], *funcs: List[Callable[[T2], R]]) -> Iterator[Iterator[R]]:
    pass
def chain_map_items(coll: Iterable[Iterable[T]], *funcs: Callable[[T2], R]) -> Iterator[Iterator[R]]:
    """
    Chain methods mapping for the given iterable.
    The shortest analogues using the standard Python methods are:
    ```python
    gen = ((func5(func4(func3(func2(func1(el))))) for el in it) for it in coll)
    gen = map(lambda it: map(lambda el: func5(func4(func3(func2(func1(el))))), it), coll)
    # Compare with:
    gen = chain_map_items(coll, func1, func2, func3, func4, func5)
    ```
    Sometimes it may not be shorter, but takes a way less number for braces to play with.
    
    Note that unlike the analogues, this first applies func1 to all elements and only then proceeds to func2. On paper.
    In practice, it is all lazy computations.
    
    Examples:
        Calculate len of hex representation of the given list of lists of numbers inputted as string:
        ```python
        numbers = [ [ '1','2','3','4' ], [ '10', '21', '42', '63' ], [ '123', '234', '345', '999' ] ]
        chain_map_items(numbers, int, hex, len, lambda l: l - 2)
        # <computations same as for `functional.chaintools.chain_map()`>
        # Result: [ [1,1,1,1], [1,2,2,2], [2,2,3,3] ]
        
        # Is the same as:
        map_items(lambda x: len(hex(int(x))) - 2, numbers)
        ((len(hex(int(x))) - 2 for x in nums) for nums in numbers)
        ```
    
    Args:
        coll: `Iterable[T]`. A starting iterable for the sequence of maps.
        *funcs: Any number of functions to be chained. Left-most functions are applied first.
    
    Returns:
        Returns an iterable containing the results of the last function application.
    """
    
    # noinspection PyTypeChecker
    return reduce(invmap_items, funcs, coll)


__all__ = \
[
    'apply',
    'apply_items',
    'chain',
    'chain_map',
    'chain_map_items',
    'chunks',
    'invcall',
    'invmap',
    'invmap_items',
    'map_items',
]
