class Limit :
    """Object for storing limit and offset of query operation. Used in LIMIT and OFFSET query
    Object properties:
    - Limit number
    - Offset number
    """

    NOT_SET = -1

    def __init__(self, limit: int, offset: int) :
        self.__limit = limit
        self.__offset = offset

    def limit(self) -> int :
        """Get limit number."""
        return self.__limit

    def offset(self) -> int :
        """Get offset number."""
        return self.__offset

    @classmethod
    def create(cls, limit, offset) :
        """Create Limit object from input limit and offset for LIMIT query."""
        validLimit = Limit.NOT_SET
        validOffset = Limit.NOT_SET
        if isinstance(limit, int) :
            if limit > 0 : validLimit = limit
        if isinstance(offset, int) :
            if offset > 0 : validOffset = offset
        return Limit(validLimit, validOffset)
