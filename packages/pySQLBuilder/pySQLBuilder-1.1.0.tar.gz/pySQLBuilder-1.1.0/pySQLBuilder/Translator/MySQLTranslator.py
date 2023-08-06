from .BaseTranslator import BaseTranslator
from ..QueryObject import QueryObject
from ..Builder import SelectBuilder, InsertBuilder, UpdateBuilder, DeleteBuilder

class MySQLTranslator(BaseTranslator) :

    def __init__(self, query: QueryObject) :
        query.setMarkQuote("?", ":", "\"")
        self.quote_struct = "`"
        self.quote_string = "'"
        self.equal = "="
        self.open_bracket = "("
        self.close_bracket = ")"
        self.dot = "."
        self.comma = ", "
        self.end_query = ";"

    def translateSelect(self, query: QueryObject, builder: SelectBuilder) :
        self.firstKeyword(query, builder.builderType())
        self.columnsSelect(query, builder.getColumns(), builder.countColumns())
        self.fromTable(query, builder.getTable())
        self.where(query, builder.getWhere(), builder.countWhere())
        self.groupBy(query, builder.getGroup(), builder.countGroup())
        self.having(query, builder.getHaving(), builder.countHaving())
        self.orderBy(query, builder.getOrder(), builder.countOrder())
        self.limitOffset(query, builder.getLimit(), builder.hasLimit())

    def translateInsert(self, query: QueryObject, builder: InsertBuilder) :
        self.firstKeyword(query, builder.builderType())
        self.intoTable(query, builder.getTable())
        self.columnsInsert(query, builder.getValues(), builder.countValues())
        self.valuesInsert(query, builder.getValues(), builder.countValues())
        self.limitOffset(query, builder.getLimit(), builder.hasLimit())

    def translateUpdate(self, query: QueryObject, builder: UpdateBuilder) :
        self.firstKeyword(query, builder.builderType())
        self.tableSet(query, builder.getTable())
        self.valuesUpdate(query, builder.getValues(), builder.countValues())
        self.where(query, builder.getWhere(), builder.countWhere())
        self.limitOffset(query, builder.getLimit(), builder.hasLimit())

    def translateDelete(self, query: QueryObject, builder: DeleteBuilder) :
        self.firstKeyword(query, builder.builderType())
        self.fromTable(query, builder.getTable())
        self.where(query, builder.getWhere(), builder.countWhere())
        self.limitOffset(query, builder.getLimit(), builder.hasLimit())
