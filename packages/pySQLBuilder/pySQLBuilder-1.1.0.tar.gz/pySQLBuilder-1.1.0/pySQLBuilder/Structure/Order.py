from .Column import Column

class Order :

    ORDER_NONE = 0
    ORDER_ASC = 1
    ORDER_DESC = 2

    def __init__(self, column: Column, orderType: int) :
        self.__column = column
        self.__orderType = orderType

    def column(self) -> Column :
        return self.__column

    def orderType(self) -> int :
        return self.__orderType

    @classmethod
    def create(cls, column, orderType) :
        columnObject = Column.create(column)
        validType = cls.getOrderType(orderType)
        return Order(columnObject, validType)

    @classmethod
    def getOrderType(cls, orderType) -> int :
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
