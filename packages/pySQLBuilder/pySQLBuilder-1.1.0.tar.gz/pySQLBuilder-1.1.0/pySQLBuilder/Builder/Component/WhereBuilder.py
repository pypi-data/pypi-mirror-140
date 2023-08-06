from ...Structure import Clause

class WhereBuilder :

    def __init__(self) :
        self.__where = ()

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
