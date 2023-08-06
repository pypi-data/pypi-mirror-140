from ...Structure import Order

class OrderByBuilder :

    def __init__(self) :
        self.__orderBy = ()

    def getOrder(self) -> tuple :
        return self.__orderBy

    def countOrder(self) -> int :
        return len(self.__orderBy)

    def addOrder(self, orderBy: Order) :
        self.__orderBy = self.__orderBy + (orderBy,)
