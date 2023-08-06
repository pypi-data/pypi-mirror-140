from .BaseBuilder import BaseBuilder
from .Structure import Limit

class InsertBuilder(BaseBuilder) :

    def __init__(self) :
        BaseBuilder.__init__(self)
        self.__limit = None

    def getLimit(self) -> tuple :
        return self.__limit

    def hasLimit(self) -> bool :
        if self.__limit is None : return False
        else : return True

    def setLimit(self, limit: Limit) :
        self.__limit = limit
