from .BaseQuery import BaseQuery
from .Component import Clauses, Where, Having, GroupBy, OrderBy, LimitOffset
from ..Builder import BaseBuilder, SelectBuilder
from ..Structure import Table, Column
from typing import Iterable, Mapping

class Select(BaseQuery, Clauses, Where, Having, GroupBy, OrderBy, LimitOffset) :

    def __init__(self, translator: int, bindingOption: int) :
        BaseQuery.__init__(self)
        self.builder = SelectBuilder()
        self.builder.builderType(BaseBuilder.SELECT)
        self.translator = translator
        self.bindingOption = bindingOption
        Clauses.__init__(self)
        Where.__init__(self)
        Having.__init__(self)
        GroupBy.__init__(self)
        OrderBy.__init__(self)
        LimitOffset.__init__(self)

    def select(self, table) :
        if table :
            tableObject = Table.create(table)
            self.builder.setTable(tableObject)
        else :
            raise Exception("Table name is not defined")
        return self

    def column(self, column) :
        columnObject = Column.create(column)
        self.builder.addColumn(columnObject)
        return self

    def columns(self, columns) :
        columnObjects = ()
        if isinstance(columns, str) :
            columnObjects += (Column.create(columns),)
        elif isinstance(columns, Mapping) :
            for key in columns.keys() :
                columnObjects += (Column.create({key: columns[key]}),)
        elif isinstance(columns, Iterable) :
            for col in columns :
                columnObjects += (Column.create(col),)
        for col in columnObjects :
            self.builder.addColumn(col)
        return self
