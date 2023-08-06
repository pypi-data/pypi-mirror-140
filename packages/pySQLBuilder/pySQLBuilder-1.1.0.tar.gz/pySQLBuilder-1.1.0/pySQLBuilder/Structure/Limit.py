class Limit :

    NOT_SET = -1

    def __init__(self, limit: int, offset: int) :
        self.__limit = limit
        self.__offset = offset

    def limit(self) -> int :
        return self.__limit

    def offset(self) -> int :
        return self.__offset

    @classmethod
    def create(cls, limit, offset) :
        validLimit = Limit.NOT_SET
        validOffset = Limit.NOT_SET
        if isinstance(limit, int) :
            if limit > 0 : validLimit = limit
        if isinstance(offset, int) :
            if offset > 0 : validOffset = offset
        return Limit(validLimit, validOffset)
