class Eq:
    """Checks for equality between a resource attribute and the given value"""
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __call__(self, resource):
        return getattr(resource, self.key) == self.value


class And:
    """Combines multiple conditions and returns true if all are true"""
    def __init__(self, filters_):
        self.filters = filters_

    def __call__(self, resource):
        return all([f(resource) for f in self.filters])


class Nop:
    """Returns True for any resource"""
    def __call__(self, resource):
        return True


def filter_spec_to_function(filter_spec):
    """Converts a filter specification into a function object that can be
    used as a filter (True if satisfies, False if not)"""
    if filter_spec is None:
        return Nop()

    if isinstance(filter_spec, dict):
        filters = []

        for key, value in filter_spec.items():
            filters.append(Eq(key, value))

        return And(filters)
    else:
        raise ValueError("Unsupported spec {}".format(filter_spec))
