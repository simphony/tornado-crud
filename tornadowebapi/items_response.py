from traitlets import HasTraits, List, Int


class ItemsResponse(HasTraits):
    """This class can be returned by items() to inform about the nature of
    the response, especially when partial, e.g. how many total items actually
    exist, and which ones are returned."""

    #: A list of the items
    items = List()

    #: The index of the first item in the above list in the complete data
    #: store. None is allowed and means Unknown
    offset = Int(None, min=0, allow_none=True)

    #: The number of items in the above list. Generally trivial but available
    #: for future expansion to using a generator.
    limit = Int(0, min=0)

    #: The total number of items available. None is allowed and means unknown.
    total = Int(0, min=0, allow_none=True)
