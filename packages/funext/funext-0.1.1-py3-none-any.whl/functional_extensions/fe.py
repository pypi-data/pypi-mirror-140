import copy
import inspect
import types
import typing
from itertools import filterfalse
import funcy
from funcy.primitives import EMPTY


# Abstract Base Classes


class Object:
    def pipe_(self, function, *args, **kwargs): return function(self, *args, **kwargs)
    def copy_(self): return copy.copy(self)
    def deepcopy_(self): return copy.deepcopy(self)
    def type_(self): return type(self)


class Function(Object, typing.Callable):
    def __init__(self, inner_function):
        self._inner_function = inner_function

    def __call__(self, *args, **kwargs):
        return self._inner_function(*args, **kwargs)

    def compose_(self, function):
        return Function(funcy.compose(function, self))

    def and_(self, other_function):
        return Function(funcy.all_fn(self, other_function))

    def or_(self, other_function):
        return Function(funcy.any_fn(self, other_function))

    def not_(self):
        return Function(funcy.complement(self))

    def partial_(self, *args, **kwargs):
        return Function(funcy.partial(self, *args, **kwargs))

    def curry_(self, n=EMPTY):
        return Function(funcy.curry(self, n))

    def complement_(self):
        return Function(funcy.complement(self))

    def all_fn_(self, *fs):
        return Function(funcy.all_fn(self, *fs))

    def any_fn_(self, *fs):
        return Function(funcy.any_fn(self, *fs))

    def none_fn_(self, *fs):
        return Function(funcy.none_fn(self, *fs))

    def one_fn_(self, *fs):
        return Function(funcy.one_fn(self, *fs))


class Container(Object, typing.Container):
    pass


class Iterable(Object, typing.Iterable):
    def to_list_(self): return List(self)
    def to_set_(self): return Set(self)
    def to_tuple_(self): return Tuple(self)

    def map_(self, function, *args, **kwargs) -> 'Iterable':
        ctor = initializers[type(self)]
        return ctor(function(element, *args, **kwargs) for element in self)

    def for_each_(self, function, *args, **kwargs):
        for x in self:
            function(x, *args, **kwargs)
        return self

    def min_(self): return min(self)
    def max_(self): return max(self)
    def sum_(self): return sum(self)
    def all_(self) -> bool: return all(self)
    def any_(self) -> bool: return any(self)
    def enumerate_(self, start=0) -> 'Enumerate':
        return Enumerate(self, start=start)
    def zip_(self, *iterables) -> 'Zip':
        return Zip(self, *iterables)

    def sort_(self, key=None, reverse=False) -> 'List':
        return List(sorted(self, key=key, reverse=reverse))
    def filter_(self, condition) -> 'Iterable':
        ctor = initializers[type(self)]
        return ctor(filter(condition, self))

    def filterfalse_(self, condition) -> 'Iterable':
        ctor = initializers[type(self)]
        return ctor(filterfalse(condition, self))


class Iterator(Iterable, typing.Iterator):
    pass


class Reversible(Object, typing.Reversible):
    def reverse_(self):
        ctor = initializers[type(self)]
        return ctor(reversed(self))


class Sized(Object, typing.Sized):
    def len_(self): return len(self)


class Collection(Sized, Iterable, Container, typing.Collection):
    pass


class Sequence(Reversible, Collection, typing.Sequence):
    def first_(self) -> typing.Any:
        return self[0]

    def last_(self) -> typing.Any:
        return self[-1]

class MutableSequence(Sequence, typing.MutableSequence):
    def map_inplace_(self, apply, *args, **kwargs):
        """Projects each element of the List to a new element and mutates the
        list in place."""
        for i, item in enumerate(iter(self)):
            self[i] = apply(item, *args, *kwargs)
        return self


class Mapping(Collection, typing.Mapping):
    pass


# Implementations

class List(list, MutableSequence, typing.List):
    def sort_inplace_(self, key=None, reverse=False):
        """sorts the list inplace and returns it"""
        super().sort(key=key, reverse=reverse)
        return self


class Dict(dict, Mapping, typing.Dict):
    pass


class Set(set, Collection, typing.Set):
    pass


class Map(map, Iterator):
    pass


class Enumerate(enumerate, Iterator):
    pass


class Zip(zip, Iterator):
    pass


class Tuple(tuple, Sequence, typing.Tuple):
    pass


def initialize_extended_list(*values):
    # case _l is called with a container or iterable instance
    if len(values) == 1 and isinstance(values[0], (typing.Container, typing.Iterable)):
        return List(values[0])
    # case _l is called with multiple individual values
    return List(values)

def initialize_extended_object(instance):
    """
    monkey-patches all functions that we want to have on a normal object onto
    the instance
    """
    methods = [member for member in inspect.getmembers(Object)
               if not member[0].startswith('__')]
    for method in methods:
        if hasattr(instance, method[0]):
            raise AttributeError(f'cannot extend {instance}, because it already has'
                                 f'a method called {method[0]}')
        setattr(instance, method[0], types.MethodType(method[1], instance))
    return instance

t_ = Tuple
m_ = Map
s_ = Set
d_ = Dict
f_ = Function
l_ = initialize_extended_list
o_ = initialize_extended_object

initializers = {
    Tuple: t_,
    Map: m_,
    Set: s_,
    Dict: d_,
    List: l_,
}