from ...Structure import Clause

class HavingBuilder :
    """Builder component for HAVING clause query
    """

    def __init__(self) :
        self.__having = ()

    def getHaving(self) -> tuple :
        """Get list of having clause"""
        return self.__having

    def lastHaving(self) -> Clause :
        """Get last having clause in having list"""
        count = len(self.__having)
        if count > 0 :
            return self.__having[count-1]
        return None

    def countHaving(self) -> int :
        """Count list of having clause"""
        return len(self.__having)

    def addHaving(self, having: Clause) :
        """Add a having clause to having list"""
        self.__having += (having,)
