import copy

from tornadowebapi.resource import Resource
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

    #: The type to check for the items. None means any type.
    _type = Type(klass=Resource, allow_none=True)

    def __init__(self, type, **kwargs):
        """Instantiates the ItemsResponse for a specific type
        of items.

        Parameters
        ----------
        type: Resource or None
            A Resource
        """
        self._type = type
        super().__init__(**kwargs)

    def set(self, lst, offset=None, total=None):
        """Sets the content of the object from a list.

        Parameters
        ----------
        lst: list
            The list of the response. It will be shallow copied into
            self.items

        offset: int or None
            THe offset of the data, for partial responses. If None, it will be
            zero by default

        total: int or None
            the total number of items, for a partial response. If None, it will
            default to the length of the passed list.

        Raises
        ------
        TypeError
            If the type of the elements in the list do not match
            with the declared type.
        """
        # Do a shallow copy without compromising the trait checks.
        self.items = copy.copy(lst)
        self._check_list_types(self.items)

        self.offset = 0 if offset is None else offset
        self.total = len(self.items) if total is None else total

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
