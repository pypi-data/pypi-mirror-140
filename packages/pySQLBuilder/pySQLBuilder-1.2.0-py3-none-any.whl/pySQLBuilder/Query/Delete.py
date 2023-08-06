from .BaseQuery import BaseQuery
from .Component import Clauses, Where, LimitOffset
from ..Builder import BaseBuilder, DeleteBuilder
from ..Structure import Table

class Delete(BaseQuery, Clauses, Where, LimitOffset) :
    """DELETE query manipulation class.
    Components:
    - Table
    - Where clause
    - Limit query
    """

    def __init__(self, translator: int, bindingOption: int) :
        BaseQuery.__init__(self)
        self.builder = DeleteBuilder()
        self.builder.builderType(BaseBuilder.DELETE)
        self.translator = translator
        self.bindingOption = bindingOption
        Clauses.__init__(self)

    def delete(self, table) :
        """DELETE query table input"""
        if table :
            tableObject = Table.create(table)
            self.builder.setTable(tableObject)
        else :
            raise Exception("Table name is not defined")
        return self
