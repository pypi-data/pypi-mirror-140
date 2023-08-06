from .BaseQuery import BaseQuery
from .Component import Clauses, Where, LimitOffset, JoinTable
from ..Builder import BaseBuilder, UpdateBuilder
from ..Structure import Table, Value

class Update(BaseQuery, Clauses, Where, LimitOffset, JoinTable) :
    """UPDATE query manipulation class.
    Components:
    - Table
    - Update values
    - Where clause
    - Join table query
    - Limit query
    """

    def __init__(self, translator: int, bindingOption: int) :
        BaseQuery.__init__(self)
        self.builder = UpdateBuilder()
        self.builder.builderType(BaseBuilder.UPDATE)
        self.translator = translator
        self.bindingOption = bindingOption
        Clauses.__init__(self)
        JoinTable.__init__(self)

    def update(self, table) :
        """UPDATE query table input"""
        if table :
            tableObject = Table.create(table)
            self.builder.setTable(tableObject)
        else :
            raise Exception("Table name is not defined")
        return self

    def set(self, values) :
        """Add value and column pair set to builder object.
        
        Takes a dictionary with keys as column or list of two list with first item as column.
        """
        valueObject = Value.create(values)
        self.builder.addValue(valueObject)
        return self
