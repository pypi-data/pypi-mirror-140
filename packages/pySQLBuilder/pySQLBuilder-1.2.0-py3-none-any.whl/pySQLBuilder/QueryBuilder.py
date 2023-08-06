from .Query import BaseQuery, Select, Insert, Update, Delete
from .QueryTranslator import QueryTranslator

class QueryBuilder :

    table = ''

    options = ()
    statement = None

    def __init__(self, translator: int = QueryTranslator.TRANSLATOR_GENERIC, bindingOption: int = QueryTranslator.PARAM_NUM) :
        self.options = (translator, bindingOption)
        self.statement = None

    def setStatement(self, statement) :
        self.statement = statement

    def setTable(self, table: str) :
        self.table = table
        return self

    def select(self, table = None) -> Select :
        if table is None :
            table = self.table
        selectQuery = Select(self.options, self.statement)
        return selectQuery.select(table)

    def insert(self, table = None) -> Insert :
        if table is None :
            table = self.table
        insertQuery = Insert(self.options, self.statement)
        return insertQuery.insert(table)

    def update(self, table = None) -> Update :
        if table is None :
            table = self.table
        updateQuery = Update(self.options, self.statement)
        return updateQuery.update(table)

    def delete(self, table = None) -> Delete :
        if table is None :
            table = self.table
        deleteQuery = Delete(self.options, self.statement)
        return deleteQuery.delete(table)
