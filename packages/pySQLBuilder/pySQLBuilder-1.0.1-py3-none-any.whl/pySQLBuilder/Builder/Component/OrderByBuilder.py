from ...Structure import Order

class OrderByBuilder :
    """Builder component for ORDER BY query
    """

    def __init__(self) :
        self.__orderBy = ()

    def getOrder(self) -> tuple :
        """Get query result order list"""
        return self.__orderBy

    def countOrder(self) -> int :
        """Count query result order list"""
        return len(self.__orderBy)

    def addOrder(self, orderBy: Order) :
        """Add a query result order to order list"""
        self.__orderBy = self.__orderBy + (orderBy,)
