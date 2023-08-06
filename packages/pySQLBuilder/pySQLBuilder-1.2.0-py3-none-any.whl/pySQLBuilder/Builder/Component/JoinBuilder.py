from ...Structure import Join

class JoinBuilder :
    """Builder component for JOIN query
    """

    def __init__(self) :
        self.__join = ()

    def getJoin(self) -> tuple :
        """Get list of join table"""
        return self.__join

    def lastJoin(self) -> Join :
        """Get last join in where list"""
        count = len(self.__join)
        if count > 0 :
            return self.__join[count-1]
        return None

    def countJoin(self) -> int :
        """Count list of join table"""
        return len(self.__join)

    def addJoin(self, join: Join) :
        """Add a join to join list"""
        self.__join += (join,)
