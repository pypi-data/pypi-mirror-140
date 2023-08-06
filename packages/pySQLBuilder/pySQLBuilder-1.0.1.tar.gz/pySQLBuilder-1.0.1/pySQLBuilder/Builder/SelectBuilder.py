from .BaseBuilder import BaseBuilder
from .Structure import Column, Clause, Order, Limit

class SelectBuilder(BaseBuilder) :

    def __init__(self) :
        BaseBuilder.__init__(self)
        self.__where = ()
        self.__having = ()
        self.__groupBy = ()
        self.__orderBy = ()
        self.__limit = None

    def getWhere(self) -> tuple:
        return self.__where

    def lastWhere(self) -> Clause :
        count = len(self.__where)
        if count > 0 :
            return self.__where[count-1]
        return None

    def countWhere(self) -> int :
        return len(self.__where)

    def addWhere(self, where: Clause) :
        self.__where += (where,)

    def editWhereNested(self, nestedLevel: int) :
        count = len(self.__where)
        if count > 0 :
            self.__where[count-1].nestedLevel(nestedLevel)

    def getHaving(self) -> tuple :
        return self.__having

    def lastHaving(self) -> Clause :
        count = len(self.__having)
        if count > 0 :
            return self.__having[count-1]
        return None

    def countHaving(self) -> int :
        return len(self.__having)

    def addHaving(self, having: Clause) :
        self.__having += (having,)

    def editHavingNested(self, nestedLevel: int) :
        count = len(self.__having)
        if count > 0 :
            self.__having[count-1].nestedLevel(nestedLevel)

    def getGroup(self) -> tuple :
        return self.__groupBy

    def countGroup(self) -> int :
        return len(self.__groupBy)

    def addGroup(self, groupBy: Column) :
        self.__groupBy = self.__groupBy + (groupBy,)

    def getOrder(self) -> tuple :
        return self.__orderBy

    def countOrder(self) -> int :
        return len(self.__orderBy)

    def addOrder(self, orderBy: Order) :
        self.__orderBy = self.__orderBy + (orderBy,)

    def getLimit(self) -> tuple :
        return self.__limit

    def hasLimit(self) -> bool :
        if self.__limit is None : return False
        else : return True

    def setLimit(self, limit: Limit) :
        self.__limit = limit
