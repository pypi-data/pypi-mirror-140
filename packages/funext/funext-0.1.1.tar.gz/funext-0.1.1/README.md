# Functional Extensions
**for Python**

https://pypi.org/project/funext/

This repository aims to extend the Python programming language by adding some
useful (functional) extensions to objects, functions and data structures. Some
of those extensions include:

- being able to chain pure (and mutating) functions by calling them directly 
  on objects. Most of those functions are known from the built-in functions.
 
- applying functions to objects and chaining them through a pipe-function

- composing functions 

## Usage

```python
from functional_extensions import l_, s_, d_, t_, f_

regular_list = [1, 2, 3, 4]
extended_list = l_(1, 2, 3, 4)

# all extended classes have a simple initializer function. Containers can either
# take individual values as *args, or a regular collection
extended_list = l_([1, 2, 3, 4]) # or
extended_list = l_(1, 2, 3, 4)

extended_set = s_(1, 2, 3, 4) # or
extended_set = s_(set(1, 2, 3, 4))

extended_dict = d_({'key': 'value'})

extended_tuple = t_(1, 2, 3, 4) # or
extended_tuple = t_((1, 2, 3, 4))

def add(a, b): return a + b
extended_function = f_(add)
```
## Available functions
### Object


```python
pipe_(self, function, *args, **kwargs)
``` 

Applies the object `self` to a function `function` with the arguments from `*args` 
and `**kwarngs` and returns the result.

---

```python
copy_(self) 
deepcopy_(self)
``` 

Copies `self`, either shallowly or deeply, and returns the result.

---

```python
type_(self)
```

Returns `type(self)`.

### Sequences and Containers

#### Iterable
```python
to_list_(self)
to_set_(self)
to_tuple_(self)
```

Converts the iterable `self` into the desired object.

---

```python
map_(self, function, *args, **kwargs)
```

Applies every element of `self` to `function` and returns an iterable of the new
elements. Passes `*args` and `**kwargs` to the map-`function`.

Returns an object of the same type as that of `self`.

---

```python
for_each_(self, apply, *args, **kwargs)
```

For every element in `self`, `function` is called with said element, as well
as `*args` and `**kwargs`. The list is then returned.

---

```python
min_(self)
max_(self)
sum_(self)
all_(self)
any_(self)
```


Returns `min(self)`, `max(self)`, `sum(self)`, `all(self)` and `any(self)` respectively.

--- 

```python
sort_(self, key=None, reverse=False)
```

Sorts all elements from the iterable `self` in a new list and returns it. Calls
the `sorted`-function under the hood with `key` and `reverse`.

---

```python
enumerate_(self, start=0)
``` 

Returns an enumerate object from the iterable `self`.

--- 

```python
zip_(self, *iterables)
```

Iterates over `self` and all iterables in `*iterables`, producing tuples with
an item from each one.

--- 

```python
filter_(self, condition)
filterfalse_(self, condition)
```

`filter_` returns a new instance of this iterable with only the elements that
`condition` returns true.

`filterfalse_`returns a new instance of this iterable
with only the elements that `condition` returns false.

#### Reversible

```python
reverse_(self)
```

Returns a new instance of the reversed iterable `self`.

#### Sized

```python
len_(self)
```

Returns `len(self)`

#### MutableSequence

```python
map_inplace_(self, apply, *args, **kwargs)
```

Applies every element of `self` to `function` and overwrites this element with
the new value.


#### List


```python
sort_inplace_(self, key=None, reverse=False)
```

Sorts the list in-place and returns the sorted list

### Functions

```python
compose_(self, function)
```

Composes a function

---

```python
and_(self, other_function)
or_(self, other_function)
not_(self)
```

Composes two predicates.

---

```python
partial_(self, *args, **kwargs)
```

Partially applys `*args`, and `**kwargs` to `self` and returns the partial 
function.

---

```python
curry_(self, n=EMPTY)
```

Curries `self`.

---

```python
complement_(self)
```

Cunstructs a negation of `self`.

---

```python
all_fn_(self, *fs)
any_fn_(self, *fs)
none_fn_(self, *fs)
one_fn_(self, *fs)
```

Construct a predicate returning `True` when all, any, none or exactly one of 
`self` and `fs` return True. 

## Examples

Most of those functions should not need additional examples, as they are a mere
re-phrasing of some basic concepts and functions of the Python programming 
language and funcy.

If you need an example anyway, you should consider looking at the test
classes, which cover every function.


## The why
An excerpt of the "zen of python":

> Beautiful is better than ugly

A simple exercise. Initialize a list with the numbers `[4, 1, 2, 3]`, take the negative
square of these numbers, sort the list and print every element individually.

Which one of the following code pieces is more beautiful?
```python
input = [4, 1, 2, 3]
squared = [-(x ** 2) for x in input]
squared.sort()
for element in squared:
  print(x)
```

```python
def negative_square(x): return - (x ** 2)

l_(4, 1, 2, 3) \
    .map_inplace_(negative_square) \
    .sort_() \
    .for_each_(print) 
```

There are 4 things happening. In the top example, all things are expressed via
a slightly different syntax. Initialization with a list literal, mapping by a 
list comprehension, calling the sort-function on the list and then printing all
elements 

In the bottom example, every "thing" that is happening, is expressed in a 
coherent way - by calling a function.

| Requirement                                       | Corresponding Function                        |
|---------------------------------------------------|-----------------------------------------------|
| Initialize a list with the numbers `[4, 1, 2, 3]` | `l_(4, 1, 2, 3)`                              |
| Take the negative square                          | `.map_inplace_(negative_square)` <sup>1</sup> |
| Sort the list                                     | `.sort_()`                                    |
| Print every element individually                  | `.for_each_(print)`                           |

<sup>1</sup> we could also use a lambda-function in-place to avoid having to
declare an own function for this case. However, the code might become slightly
less expressive. Which brings us to the next "principle"

> Explicit is better than implicit

This principle means, that there shouldn't be anything unexpected happening under
the hood, which is often the case in high-level codebases. Metaprogramming,
making use of inheritance or just not choosing proper variable names can make
the code hard to read and understand, making it more easy to make mistakes.

These extensions might make things more complex at first glance, but the naming
is chosen quite carefully. If a function name corresponds to a name of a
built-in function, this functions will not do more or less than exactly that
function.

All other functions are designed to be pure, and not cause anything to happen
outside of their little scope.

All function that are not pure, are explicitly named like that, for example
`map_inplace_`

All functions that have similar names than built-in functions, have an 
explicit "_"-postfix to denote that they do things differently, for example
`sort_`, which adheres to the rule that functions are pure, unlike the `sort()`-
function from the builtin `list`-class.

> Simple is better than complex

and

> Readability counts
 
One might argue, that any code which doesn't directly solves a certain use case
is, by definition, not simple. It might be correct to define complexity like that.
But you can also define complexity by how much time it takes you to read and 
understand code. This library tries to help reduce complexity of the code itself,
on a less abstract layer than the use-case-specific solutions are written in. By
that, hopefully those solutions also become less complex.

> There should be one-- and preferably only one --obvious way to do it.

Yes, in an attempt to fulfill other principles, this principle is arguably 
broken. Now there is one more way to write a for-loop or call a map-function.
At least I try to keep this rule fulfilled within this library. There should
be one obvious way to do one thing by using functional extensions.

