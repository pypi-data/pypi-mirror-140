import typing
from unittest import TestCase

import attr

from src.functional_extensions import fe
from src.functional_extensions.fe import l_, o_, f_


class TestList(TestCase):
    def test_ctor(self) -> None:
        expected = [1, 2, 3, 4]
        actual = l_([1, 2, 3, 4])
        actual2 = l_(1, 2, 3, 4)
        self.assertTrue(expected == actual == actual2)

    def test_sort_inplace_with_ints(self) -> None:
        expected = [1, 2, 3, 4]
        actual = l_(3, 4, 1, 2)
        actual2 = actual.sort_inplace_()
        self.assertEqual(expected, actual)
        self.assertIs(actual, actual2)

        expected = [4, 3, 2, 1]
        actual = l_(3, 4, 1, 2)
        actual2 = actual.sort_inplace_(reverse=True)
        self.assertEqual(expected, actual)
        self.assertIs(actual, actual2)

    def test_sort_with_ints(self) -> None:
        expected = [1, 2, 3, 4]
        unsorted = l_(3, 4, 1, 2)
        sorted = unsorted.sort_()
        self.assertEqual(expected, sorted)
        self.assertIsNot(unsorted, sorted)

        expected = [4, 3, 2, 1]
        unsorted = l_(3, 4, 1, 2)
        sorted = unsorted.sort_(reverse=True)
        self.assertEqual(expected, sorted)
        self.assertIsNot(unsorted, sorted)

    def test_any_with_bools(self) -> None:
        self.assertTrue(l_(True, False, False).any_())
        self.assertFalse(l_(False, False, False).any_())

    def test_sort_with_predicate(self) -> None:
        @attr.s(auto_attribs=True)
        class Student:
            name: str
            grade: str
            age: int

        john = Student('john', 'A', 15)
        jane = Student('jane', 'B', 12)
        dave = Student('dave', 'B', 10)
        students = [john, jane, dave]

        expected = [dave, jane, john]
        actual = l_(students).sort_inplace_(key=lambda student: student.age)
        self.assertEqual(expected, actual)

    def test_filter(self) -> None:
        numbers = [1, 2, 3, 4]

        def is_even(number): return number % 2 == 0

        expected = [2, 4]
        actual = l_(numbers).filter_(is_even)
        self.assertEqual(expected, actual)

    def test_filterfalse(self) -> None:
        numbers = [1, 2, 3, 4]

        def is_even(number): return number % 2 == 0

        expected = [1, 3]
        actual = l_(numbers).filterfalse_(is_even)
        self.assertEqual(expected, actual)

    def test_map_with_int_list(self) -> None:
        def square(x): return x ** 2

        expected = [1, 0, 1, 4]
        actual = l_(-1, 0, 1, 2).map_(square).to_list_()
        self.assertEqual(expected, actual)

        expected = l_(-1, 0, 1, 2)
        actual = expected.map_(square).to_list()
        self.assertNotEqual(expected, actual)

    def test_map_with_int_list(self) -> None:
        def multiply(x, y): return x * y

        expected = [2, 4, 6, 8]
        actual = l_(1, 2, 3, 4).map_(multiply, 2)
        self.assertEqual(expected, actual)

    def test_map_inplace_with_int_list(self) -> None:
        def square(x): return x ** 2

        expected = [1, 0, 1, 4]
        actual = l_(-1, 0, 1, 2).map_inplace_(square)
        self.assertEqual(expected, actual)

        expected = l_(-1, 0, 1, 2)
        actual = expected.map_inplace_(square)
        self.assertEqual(expected, actual)

    def test_for_each_with_int_list(self) -> None:
        class ReduceBySum:
            def __init__(self):
                self.sum = 0

            def __call__(self, summand: int) -> None:
                self.sum += summand

        reduce_by_sum_regular = ReduceBySum()
        for element in [-1, 0, 1, 2]:
            reduce_by_sum_regular(element)

        reduce_by_sum_extended = ReduceBySum()
        l_(-1, 0, 1, 2).for_each_(reduce_by_sum_extended)

        self.assertTrue(reduce_by_sum_regular.sum ==
                        reduce_by_sum_extended.sum ==
                        2)

    def test_pipe_with_int_list(self) -> None:
        class CollectSum:
            def __init__(self):
                self.sum = 0

            def __call__(self, l: typing.List) -> None:
                self.sum = sum(l)

        collect_sum = CollectSum()
        l_(-1, 0, 1, 2).pipe_(collect_sum)
        expected = 2
        actual = collect_sum.sum
        self.assertEqual(expected, actual)

    def test_min_with_int_list(self) -> None:
        expected = -1
        actual = l_(4, 2, -1, 1).min_()
        self.assertEqual(expected, actual)

    def test_max_with_int_list(self) -> None:
        expected = 4
        actual = l_(4, 2, -1, 1).max_()
        self.assertEqual(expected, actual)

    def test_sum_with_int_list(self) -> None:
        expected = 6
        actual = l_(4, 2, -1, 1).sum_()
        self.assertEqual(expected, actual)

    def test_reverse_with_int_list(self) -> None:
        expected = [4, 3, 2, 1]
        actual = l_(1, 2, 3, 4).reverse_()
        self.assertEqual(expected, actual)

    def test_zip(self) -> None:
        expected = [(1, 'sugar'), (2, 'spice'), (3, 'everything nice')]

        actual = l_(1, 2, 3).zip_(['sugar', 'spice', 'everything nice']) \
                            .to_list_()

        self.assertEqual(expected, actual)

    def test_enumerate(self) -> None:
        # TODO(jonas) find a good test for the enumerate function
        pass

class TestObject(TestCase):
    def test_init_helper(self) -> None:
        @attr.s(auto_attribs=True)
        class Dog():
            name: str
            age: int

        def rename_dog(dog: Dog, new_name: str):
            dog.name = new_name
            return dog

        dog = Dog('Nick', 4)
        try:
            extended_dog = o_(dog)

            expected_renamed_dog = Dog('Jack', 4)
            actual_renamed_dog = extended_dog.pipe_(rename_dog, 'Jack')
            self.assertEqual(expected_renamed_dog, actual_renamed_dog)

            copied_dog = extended_dog.copy_()
            self.assertEqual(dog, copied_dog)
            self.assertIsNot(dog, copied_dog)

            deep_copied_dog = extended_dog.deepcopy_()
            self.assertEqual(dog, deep_copied_dog)
            self.assertIsNot(dog, deep_copied_dog)

            dog_type = extended_dog.type_()
            self.assertEqual(dog_type, Dog)
        except BaseException:
            self.fail(BaseException)

    def test_init_helper_obj_already_has_attribute(self) -> None:
        @attr.s(auto_attribs=True)
        class Dog:
            name: str
            age: int
            pipe_: typing.Any = None

        dog = Dog('Nick', 4)
        try:
            o_(dog)
            self.fail('Extended dog must not overwrite already existing pipe_-property')
        except AttributeError:
            pass

    def test_pipe_with_object(self) -> None:
        @attr.s(auto_attribs=True)
        class Dog(fe.Object):
            name: str
            age: int

        def rename_dog(dog: Dog, new_name: str):
            dog.name = new_name

        expected = Dog(name='Jack', age=4)
        actual = Dog(name='Nick', age=4)
        actual.pipe_(rename_dog, 'Jack')

        self.assertEqual(expected, actual)


class TestFunction(TestCase):
    def test_init_helper(self):
        def add(a, b): return a + b
        extended_add = f_(add)

        expected = add(1, 1)
        actual = extended_add(1, 1)
        self.assertEqual(expected, actual)

    def test_compose(self):
        def add(a, b): return a + b
        def square(a): return a ** 2

        add_and_square = f_(add).compose_(square)
        expected = square(add(1,2))
        actual = add_and_square(1, 2)
        self.assertEqual(expected, actual)

    def test_and(self):
        def is_even(a): return a % 2 == 0
        def is_divisable_by_three(a): return a % 3 == 0

        is_even_and_divisable_by_three = f_(is_even).and_(is_divisable_by_three)
        self.assertTrue(is_even_and_divisable_by_three(12))
        self.assertFalse(is_even_and_divisable_by_three(4))

    def test_or(self):
        def is_even(a): return a % 2 == 0
        def is_divisable_by_three(a): return a % 3 == 0

        is_even_or_divisable_by_three = f_(is_even).or_(is_divisable_by_three)
        self.assertTrue(is_even_or_divisable_by_three(4))
        self.assertTrue(is_even_or_divisable_by_three(3))
        self.assertTrue(is_even_or_divisable_by_three(12))
        self.assertFalse(is_even_or_divisable_by_three(7))

    def test_not(self):
        def is_even(a): return a % 2 == 0

        is_not_even = f_(is_even).not_()

        self.assertTrue(is_not_even(3))
        self.assertFalse(is_not_even(4))

    def test_partial(self):
        def multiply(a, b): return a * b

        multiply_by_three = f_(multiply).partial_(3)
        self.assertEqual(9, multiply_by_three(3))

    def test_curry(self):
        def add(a, b):
            return a + b

        curried = f_(add).curry_()
        self.assertEqual(add(3, 4), curried(3)(4))

    def test_complement(self):
        def is_even(num):
            return num % 2 == 0

        is_odd = f_(is_even).complement_()
        self.assertTrue(is_odd(4) != is_even(4))

    def test_all_fn(self):
        def is_even(num):
            return num % 2 == 0

        def is_int(num):
            return type(num) == int

        is_even_and_int = f_(is_even).all_fn_(is_int)
        self.assertTrue(is_even_and_int(2))
        self.assertFalse(is_even_and_int(2.0))
        self.assertFalse(is_even_and_int(3))
        self.assertFalse(is_even_and_int(3.0))

    def test_any_fn(self):
        def is_even(num):
            return num % 2 == 0

        def is_int(num):
            return type(num) == int

        is_even_or_int = f_(is_even).any_fn_(is_int)
        self.assertTrue(is_even_or_int(2))
        self.assertTrue(is_even_or_int(2.0))
        self.assertTrue(is_even_or_int(3))
        self.assertFalse(is_even_or_int(3.0))

    def test_none_fn(self):
        def is_even(num):
            return num % 2 == 0

        def is_int(num):
            return type(num) == int

        neither_even_nor_int = f_(is_even).none_fn_(is_int)
        self.assertFalse(neither_even_nor_int(2))
        self.assertFalse(neither_even_nor_int(2.0))
        self.assertFalse(neither_even_nor_int(3))
        self.assertTrue(neither_even_nor_int(3.0))

    def test_one_fn(self):
        def is_even(num):
            return num % 2 == 0

        def is_int(num):
            return type(num) == int

        even_xor_int = f_(is_even).one_fn_(is_int)
        self.assertFalse(even_xor_int(2))
        self.assertTrue(even_xor_int(2.0))
        self.assertTrue(even_xor_int(3))
        self.assertFalse(even_xor_int(3.0))
