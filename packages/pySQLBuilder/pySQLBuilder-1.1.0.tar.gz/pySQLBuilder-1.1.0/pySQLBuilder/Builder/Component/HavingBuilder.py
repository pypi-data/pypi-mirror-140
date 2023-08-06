from ...Structure import Clause

class HavingBuilder :

    def __init__(self) :
        self.__having = ()

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
