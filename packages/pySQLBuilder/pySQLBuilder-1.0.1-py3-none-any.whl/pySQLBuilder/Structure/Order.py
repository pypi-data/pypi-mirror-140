from .Column import Column

class Order :
    """Object for storing order of query result definition. Used in ORDER BY query
    Object properties:
    - Column object
    - Oder type
    """

    ORDER_NONE = 0
    ORDER_ASC = 1
    ORDER_DESC = 2

    def __init__(self, column: Column, orderType: int) :
        self.__column = column
        self.__orderType = orderType

    def column(self) -> Column :
        """Get order column."""
        return self.__column

    def orderType(self) -> int :
        """Get order type."""
        return self.__orderType

    @classmethod
    def create(cls, column, orderType) :
        """Create Order object from column inputs and order type for ORDER BY query."""
        if isinstance(column, Column) :
            columnObject = column
        else :
            columnObject = Column.create(column)
        validType = cls.getOrderType(orderType)
        return Order(columnObject, validType)

    @classmethod
    def getOrderType(cls, orderType) -> int :
        """Get valid order type from input order type."""
        if isinstance(orderType, int) :
            validType = orderType
        else :
            if orderType == 'ASCENDING' or orderType == 'ASC' or orderType == 'ascending' or orderType == 'asc' :
                validType = Order.ORDER_ASC
            elif orderType == 'DESCENDING' or orderType == 'DESC' or orderType == 'descending' or orderType == 'desc' :
                validType = Order.ORDER_DESC
            else :
                validType = Order.ORDER_NONE
        return validType
