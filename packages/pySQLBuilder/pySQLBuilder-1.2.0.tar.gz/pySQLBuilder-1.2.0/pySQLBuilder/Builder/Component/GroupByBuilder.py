from ...Structure import Column

class GroupByBuilder :
    """Builder component for GROUP BY query
    """

    def __init__(self) :
        self.__groupBy = ()

    def getGroup(self) -> tuple :
        """Get list of column group"""
        return self.__groupBy

    def countGroup(self) -> int :
        """Count list of column group"""
        return len(self.__groupBy)

    def addGroup(self, groupBy: Column) :
        """Add a column to group list"""
        self.__groupBy = self.__groupBy + (groupBy,)
