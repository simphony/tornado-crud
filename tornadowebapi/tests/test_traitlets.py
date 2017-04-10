import unittest

from tornadowebapi.traitlets import (
    HasTraits, Int, Absent, Unicode, Dict, List, Float, Bool)


class ProbingTable(HasTraits):
    i = Int()
    f = Float()
    l = List()
    d = Dict()
    b = Bool()
    u = Unicode()


class TestTraitlets(unittest.TestCase):
    def setUp(self):
        self.probe = ProbingTable()
        self.names_and_values = [
            ("i", 3),
            ("f", 2.0),
            ("d", {}),
            ("b", True),
            ("l", []),
            ("u", "foo")]

    def test_absent(self):
        for trait_name, value in self.names_and_values:
            self.assertEqual(getattr(self.probe, trait_name), Absent)

    def test_set_and_unset_and_set(self):
        for trait_name, value in self.names_and_values:
            self.assertEqual(getattr(self.probe, trait_name), Absent)
            setattr(self.probe, trait_name, value)
            self.assertEqual(getattr(self.probe, trait_name), value)
            setattr(self.probe, trait_name, Absent)
            self.assertEqual(getattr(self.probe, trait_name), Absent)
