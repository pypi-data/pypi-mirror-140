from .BaseQuery import BaseQuery
from .Component import Clauses, Where, LimitOffset
from ..Builder import BaseBuilder, UpdateBuilder
from ..Structure import Table, Value

class Update(BaseQuery, Clauses, Where, LimitOffset) :

    def __init__(self, translator: int, bindingOption: int) :
        BaseQuery.__init__(self)
        self.builder = UpdateBuilder()
        self.builder.builderType(BaseBuilder.UPDATE)
        self.translator = translator
        self.bindingOption = bindingOption
        Clauses.__init__(self)
        Where.__init__(self)
        LimitOffset.__init__(self)

    def update(self, table) :
        if table :
            tableObject = Table.create(table)
            self.builder.setTable(tableObject)
        else :
            raise Exception("Table name is not defined")
        return self

    def set(self, values) :
        valueObject = Value.create(values)
        self.builder.addValue(valueObject)
        return self
