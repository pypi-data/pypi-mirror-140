from .BaseBuilder import BaseBuilder
from .Component import WhereBuilder, HavingBuilder, GroupByBuilder, OrderByBuilder, LimitBuilder

class SelectBuilder(BaseBuilder, WhereBuilder, HavingBuilder, GroupByBuilder, OrderByBuilder, LimitBuilder) :

    def __init__(self) :
        BaseBuilder.__init__(self)
        WhereBuilder.__init__(self)
        HavingBuilder.__init__(self)
        GroupByBuilder.__init__(self)
        OrderByBuilder.__init__(self)
        LimitBuilder.__init__(self)
