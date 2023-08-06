from ...Structure import Column, Order
from ...Builder import OrderByBuilder

class OrderBy :
    """ORDER BY manipulation component.
    """

    def oderBy(self, columns, orderType) :
        """ORDER BY query manipulation"""
        for columnObject in Column.createMulti(columns) :
            orderObject = Order.create(columnObject, orderType)
            if isinstance(self.builder, OrderByBuilder) :
                self.builder.addOrder(orderObject)
            else :
                raise Exception('Builder object does not support ORDER BY query')
        return self

    def orderByAsc(self, columns) :
        """ORDER BY query with ASC order"""
        return self.oderBy(columns, Order.ORDER_ASC)

    def orderByDesc(self, columns) :
        """ORDER BY query with DESC order"""
        return self.oderBy(columns, Order.ORDER_DESC)
