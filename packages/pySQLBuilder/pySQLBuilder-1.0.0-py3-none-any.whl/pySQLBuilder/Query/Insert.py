from .BaseQuery import BaseQuery
from .Manipulation import Manipulation
from ..Builder import BaseBuilder, InsertBuilder

class Insert(BaseQuery) :

    man = Manipulation()

    def __init__(self, options: tuple = (), statement = None) :
        self.builder = InsertBuilder()
        self.builder.builderType(BaseBuilder.INSERT)
        self.options = options
        self.statement = statement

    def insert(self, table) :
        if table :
            tableObject = self.man.createTable(table)
            self.builder.setTable(tableObject)
        else :
            raise Exception("Table name is not defined")
        return self

    def values(self, values) :
        valueObject = self.man.createValue(values)
        self.builder.addValue(valueObject)
        return self

    def multiValues(self, multiValues) :
        valuesObjects = self.man.createMultiValue(multiValues)
        for val in valuesObjects :
            self.builder.addValue(val)
        return self

    def limit(self, limit, offset = None) :
        limitObject = self.man.createLimit(limit, offset)
        self.builder.setLimit(limitObject)
        return self

    def offset(self, offset) :
        limitObject = self.man.offset(offset)
        self.builder.setLimit(limitObject)
        return self
