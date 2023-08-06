from ...Structure import Column

class GroupByBuilder :

    def __init__(self) :
        self.__groupBy = ()

    def getGroup(self) -> tuple :
        return self.__groupBy

    def countGroup(self) -> int :
        return len(self.__groupBy)

    def addGroup(self, groupBy: Column) :
        self.__groupBy = self.__groupBy + (groupBy,)
