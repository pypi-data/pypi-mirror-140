from .BaseBuilder import BaseBuilder
from .Component import WhereBuilder, LimitBuilder

class DeleteBuilder(BaseBuilder, WhereBuilder, LimitBuilder) :
    """Template for building DELETE query
    Components:
    - Where builder
    - Limit builder
    """

    def __init__(self) :
        BaseBuilder.__init__(self)
        WhereBuilder.__init__(self)
        LimitBuilder.__init__(self)
