"""Our traits must be able to deal with Absent values, for two reasons.
First, the fact that we don't specify an optional value does not imply that
the resulting resource will have a default.

Second, when we do modification (PATCH) operations, we only specify the values
we want to change.

In practice, this means that all traits are optional. Mandatory entries
are only enforced when creating new resources or setting from scratch."""

import traitlets as _traitlets

HasTraits = _traitlets.HasTraits
TraitError = _traitlets.TraitError
Absent = _traitlets.Sentinel("Absent", "tornadowebapi.traitlets")


class Int(_traitlets.Int):
    """An int trait, with support for lack of specified value"""

    default_value = Absent

    def validate(self, obj, value):
        if value == Absent:
            return value
        return super().validate(obj, value)


class Unicode(_traitlets.Unicode):
    default_value = Absent

    def info(self):
        qualifiers = []
        if self.metadata.get("strip", False):
            qualifiers.append("strip")

        if not self.metadata.get("allow_empty", True):
            qualifiers.append("not empty")

        text = ", ".join(qualifiers)

        if len(text):
            return self.info_text + "("+text+")"
        else:
            return self.info_text

    def validate(self, obj, value):
        if value == Absent:
            return value

        value = super().validate(obj, value)

        if self.metadata.get("strip", False):
            value = value.strip()

        if not self.metadata.get("allow_empty", True) and len(value) == 0:
            self.error(obj, value)

        return value


class Bool(_traitlets.Bool):
    default_value = Absent

    def validate(self, obj, value):
        if value == Absent:
            return value
        return super().validate(obj, value)


class Float(_traitlets.Float):
    default_value = Absent

    def validate(self, obj, value):
        if value == Absent:
            return value
        return super().validate(obj, value)


class List(_traitlets.List):
    def make_dynamic_default(self):
        return Absent

    def validate(self, obj, value):
        if value == Absent:
            return value
        return super().validate(obj, value)


class Dict(_traitlets.Dict):
    def make_dynamic_default(self):
        return Absent

    def validate(self, obj, value):
        if value == Absent:
            return value
        return super().validate(obj, value)


class OneOf(_traitlets.Instance):
    """Marks a one to one relationship with a resource or resourcefragment."""
    def make_dynamic_default(self):
        return Absent

    def validate(self, obj, value):
        if value == Absent:
            return value

        return super().validate(obj, value)
