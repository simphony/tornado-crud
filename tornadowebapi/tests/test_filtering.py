import unittest

from tornadowebapi.filtering import filter_spec_to_function, And, Eq, Nop
from tornadowebapi.schema import Schema
from tornadowebapi.traitlets import Int


class Bongo(Schema):
    foo = Int()
    bar = Int()


class TestFilter(unittest.TestCase):
    def test_filtering_construction(self):
        f = filter_spec_to_function({
            "foo": 5,
            "bar": 3
        })

        self.assertIsInstance(f, And)
        self.assertEqual(len(f.filters), 2)
        self.assertIsInstance(f.filters[0], Eq)
        self.assertIsInstance(f.filters[1], Eq)

        self.assertEqual(set([eq.key for eq in f.filters]),
                         {"foo", "bar"})
        self.assertEqual(set([eq.value for eq in f.filters]),
                         {5, 3})

    def test_filters_work(self):
        b = Bongo(identifier="1")

        f = filter_spec_to_function({
            "foo": 5,
            "bar": 3
        })

        self.assertFalse(f(b))

        b.foo = 5
        self.assertFalse(f(b))

        b.bar = 3
        self.assertTrue(f(b))

    def test_empty_filtering(self):
        b = Bongo(identifier="1")

        f = filter_spec_to_function(None)
        self.assertIsInstance(f, Nop)
        self.assertTrue(f(b))

        f = filter_spec_to_function({})
        self.assertIsInstance(f, And)
        self.assertTrue(f(b))

    def test_exception(self):
        with self.assertRaises(ValueError):
            filter_spec_to_function("")
