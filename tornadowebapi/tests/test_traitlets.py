import unittest

from tornadowebapi.traitlets import (
    HasTraits, Int, Absent, Unicode, Dict, List, Float, Bool, TraitError)


class ProbingTable(HasTraits):
    i = Int()
    f = Float()
    l = List()
    d = Dict()
    b = Bool()
    u = Unicode()
    us = Unicode(strip=True)
    use = Unicode(strip=True, allow_empty=False)
    ue = Unicode(allow_empty=False)


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

    def test_unicode_strip_and_empty(self):
        self.probe.us = "  hello "
        self.assertEqual(self.probe.us, "hello")

        with self.assertRaises(TraitError):
            self.probe.ue = ""

        self.probe.ue = " "
        self.assertEqual(self.probe.ue, " ")

        with self.assertRaises(TraitError):
            self.probe.use = "   "
