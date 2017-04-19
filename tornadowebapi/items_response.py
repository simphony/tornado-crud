from traitlets import HasTraits, List, Int, Type


class ItemsResponse(HasTraits):
    """This class can be returned by items() to inform about the nature of
    the response, especially when partial, e.g. how many total items actually
    exist, and which ones are returned."""

    #: A list of the items
    items = List()

    #: The index of the first item in the above list in the complete data
    #: store.
    offset = Int(0, min=0)

    #: The total number of items available.
    total = Int(0, min=0)

    #: The type to check for the items. None means any type
    _type = Type(allow_none=True)

    def __init__(self, type, **kwargs):
        self._type = type
        super().__init__(**kwargs)

    def set(self, lst, offset=None, total=None):
        self.items = lst[:]
        self._check_list_types(self.items)

        self.offset = 0 if offset is None else offset
        self.total = len(lst) if total is None else total

    def _check_list_types(self, l):
        """Checks the list types to verify if they are all
        of the same type as self._type"""
        if self._type is None:
            return

        for entry in l:
            if not isinstance(entry, self._type):
                raise TypeError(
                    "ItemsResponse contains objects different from "
                    "the declared type. Got {} instead of {}".format(
                        entry.__class__,
                        self._type))
