from .BaseBuilder import BaseBuilder
from .Structure import Clause, Limit

class DeleteBuilder(BaseBuilder) :

    def __init__(self) :
        BaseBuilder.__init__(self)
        self.__where = ()
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

    def getLimit(self) -> tuple :
        return self.__limit

    def hasLimit(self) -> bool :
        if self.__limit is None : return False
        else : return True

    def setLimit(self, limit: Limit) :
        self.__limit = limit
