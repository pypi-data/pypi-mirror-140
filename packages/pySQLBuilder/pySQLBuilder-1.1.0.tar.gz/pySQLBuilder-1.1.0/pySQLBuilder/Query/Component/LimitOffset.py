from ...Structure import Limit
from ...Builder import LimitBuilder

class LimitOffset :

    def limit(self, limit, offset = Limit.NOT_SET) :
        limitObject = Limit.create(limit, offset)
        if isinstance(self.builder, LimitBuilder) :
            self.builder.setLimit(limitObject)
        else :
            raise Exception('Builder object does not support LIMIT and OFFSET query')
        return self

    def offset(self, offset) :
        return self.limit(Limit.NOT_SET, offset)
