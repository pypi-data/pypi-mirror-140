from .BaseTranslator import BaseTranslator
from ..QueryObject import QueryObject
from ..Builder import SelectBuilder, InsertBuilder, UpdateBuilder, DeleteBuilder

class MySQLTranslator(BaseTranslator) :
    """Translator for MySQL database.
    """

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
        """Translate SELECT query from select builder."""
        multiTableFlag = bool(builder.countJoin())
        self.firstKeyword(query, builder.builderType())
        self.columnsSelect(query, builder.getColumns(), builder.countColumns(), multiTableFlag)
        self.fromTable(query, builder.getTable())
        self.join(query, builder.getJoin())
        self.where(query, builder.getWhere(), builder.countWhere(), multiTableFlag)
        self.groupBy(query, builder.getGroup(), builder.countGroup(), multiTableFlag)
        self.having(query, builder.getHaving(), builder.countHaving(), multiTableFlag)
        self.orderBy(query, builder.getOrder(), builder.countOrder(), multiTableFlag)
        self.limitOffset(query, builder.getLimit(), builder.hasLimit())

    def translateInsert(self, query: QueryObject, builder: InsertBuilder) :
        """Translate INSERT query from insert builder."""
        self.firstKeyword(query, builder.builderType())
        self.intoTable(query, builder.getTable())
        self.columnsInsert(query, builder.getValues(), builder.countValues())
        self.valuesInsert(query, builder.getValues(), builder.countValues())
        self.limitOffset(query, builder.getLimit(), builder.hasLimit())

    def translateUpdate(self, query: QueryObject, builder: UpdateBuilder) :
        """Translate UPDATE query from update builder."""
        multiTableFlag = bool(builder.countJoin())
        self.firstKeyword(query, builder.builderType())
        self.tableSet(query, builder.getTable())
        self.join(query, builder.getJoin())
        self.valuesUpdate(query, builder.getValues(), builder.countValues(), multiTableFlag)
        self.where(query, builder.getWhere(), builder.countWhere(), multiTableFlag)
        self.limitOffset(query, builder.getLimit(), builder.hasLimit())

    def translateDelete(self, query: QueryObject, builder: DeleteBuilder) :
        """Translate DELETE query from delete builder."""
        self.firstKeyword(query, builder.builderType())
        self.fromTable(query, builder.getTable())
        self.where(query, builder.getWhere(), builder.countWhere())
        self.limitOffset(query, builder.getLimit(), builder.hasLimit())
