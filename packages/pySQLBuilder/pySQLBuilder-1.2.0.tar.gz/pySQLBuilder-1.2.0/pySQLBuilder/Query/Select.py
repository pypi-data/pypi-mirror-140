from .BaseQuery import BaseQuery
from .Component import Clauses, Where, Having, GroupBy, OrderBy, LimitOffset, JoinTable
from ..Builder import BaseBuilder, SelectBuilder
from ..Structure import Table, Column, Expression
from typing import Iterable

class Select(BaseQuery, Clauses, Where, Having, GroupBy, OrderBy, LimitOffset, JoinTable) :
    """SELECT query manipulation class.
    Components:
    - Table
    - Select columns
    - Join table query
    - Where clause
    - Group by query
    - Having clause
    - Order by query
    - Limit query
    """

    def __init__(self, translator: int, bindingOption: int) :
        BaseQuery.__init__(self)
        self.builder = SelectBuilder()
        self.builder.builderType(BaseBuilder.SELECT)
        self.translator = translator
        self.bindingOption = bindingOption
        Clauses.__init__(self)
        JoinTable.__init__(self)

    def select(self, table) :
        """SELECT query table input"""
        if table :
            tableObject = Table.create(table)
            self.builder.setTable(tableObject)
        else :
            raise Exception("Table name is not defined")
        return self

    def selectDistinct(self, table) :
        """SELECT DISTINC query table input"""
        self.builder.builderType(BaseBuilder.SELECT_DISTINCT)
        return self.select(table)

    def column(self, column) :
        """Add a column to builder object.
        
        Takes a column name string or a dictionary with keys as column alias.
        """
        columnObject = Column.create(column)
        self.builder.addColumn(columnObject)
        return self

    def columns(self, columns) :
        """Add multiple columns to builder object.
        
        Takes a list containing column name or a dictionary with keys as column alias.
        """
        for columnObject in Column.createMulti(columns) :
            self.builder.addColumn(columnObject)
        return self

    def columnExpression(self, expression, alias, params: Iterable = ()) :
        """Add an expression to list of Column in builder object.
        
        Takes expression string, expression alias, and list of parameters.
        """
        expressionObject = Expression.create(expression, alias, params)
        self.builder.addColumn(expressionObject)
        return self
