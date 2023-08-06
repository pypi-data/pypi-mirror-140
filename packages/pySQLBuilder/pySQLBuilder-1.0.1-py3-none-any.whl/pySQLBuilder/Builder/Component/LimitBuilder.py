from ...Structure import Limit

class LimitBuilder :
    """Builder component for LIMIT and OFFSET query
    """

    def __init__(self) :
        self.__limit = None

    def getLimit(self) -> tuple :
        """Get limit and offset number"""
        return self.__limit

    def hasLimit(self) -> bool :
        """Check limit or offset defined"""
        if self.__limit is None : return False
        else : return True

    def setLimit(self, limit: Limit) :
        """Set limit and offset number"""
        self.__limit = limit
