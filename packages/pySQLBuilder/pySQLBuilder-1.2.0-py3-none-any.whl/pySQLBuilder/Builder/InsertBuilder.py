from .BaseBuilder import BaseBuilder
from .Component import LimitBuilder

class InsertBuilder(BaseBuilder, LimitBuilder) :
    """Template for building INSERT query
    Components:
    - Limit builder
    """

    def __init__(self) :
        BaseBuilder.__init__(self)
        LimitBuilder.__init__(self)
