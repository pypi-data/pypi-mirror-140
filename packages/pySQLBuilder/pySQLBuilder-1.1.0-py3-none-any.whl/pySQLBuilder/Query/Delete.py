from .BaseQuery import BaseQuery
from .Component import Clauses, Where, LimitOffset
from ..Builder import BaseBuilder, DeleteBuilder
from ..Structure import Table

class Delete(BaseQuery, Clauses, Where, LimitOffset) :

    def __init__(self, translator: int, bindingOption: int) :
        BaseQuery.__init__(self)
        self.builder = DeleteBuilder()
        self.builder.builderType(BaseBuilder.DELETE)
        self.translator = translator
        self.bindingOption = bindingOption
        Clauses.__init__(self)
        Where.__init__(self)
        LimitOffset.__init__(self)

    def delete(self, table) :
        if table :
            tableObject = Table.create(table)
            self.builder.setTable(tableObject)
        else :
            raise Exception("Table name is not defined")
        return self
