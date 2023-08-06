from .BaseBuilder import BaseBuilder
from .Component import WhereBuilder, LimitBuilder

class UpdateBuilder(BaseBuilder, WhereBuilder, LimitBuilder) :

    def __init__(self) :
        BaseBuilder.__init__(self)
        WhereBuilder.__init__(self)
        LimitBuilder.__init__(self)
