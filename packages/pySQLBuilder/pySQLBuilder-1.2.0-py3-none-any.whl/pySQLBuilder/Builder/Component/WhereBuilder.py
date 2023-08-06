from ...Structure import Clause

class WhereBuilder :
    """Builder component for WHERE clause query
    """

    def __init__(self) :
        self.__where = ()

    def getWhere(self) -> tuple:
        """Get list of where clause"""
        return self.__where

    def lastWhere(self) -> Clause :
        """Get last where clause in where list"""
        count = len(self.__where)
        if count > 0 :
            return self.__where[count-1]
        return None

    def countWhere(self) -> int :
        """Count list of where clause"""
        return len(self.__where)

    def addWhere(self, where: Clause) :
        """Add a where clause to where list"""
        self.__where += (where,)
