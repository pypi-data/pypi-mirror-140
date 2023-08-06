from .BaseQuery import BaseQuery
from .Manipulation import Manipulation
from ..Builder import BaseBuilder, SelectBuilder

class Select(BaseQuery) :

    man = Manipulation()

    def __init__(self, options: tuple = (), statement = None) :
        self.builder = SelectBuilder()
        self.builder.builderType(BaseBuilder.SELECT)
        self.options = options
        self.statement = statement

    def select(self, table) :
        if table :
            tableObject = self.man.createTable(table)
            self.builder.setTable(tableObject)
        else :
            raise Exception("Table name is not defined")
        return self

    def column(self, column) :
        columnObject = self.man.createColumn(column)
        self.builder.addColumn(columnObject)
        return self

    def columns(self, columns) :
        columnObjects = self.man.createColumns(columns)
        for col in columnObjects :
            self.builder.addColumn(col)
        return self

    def beginWhere(self) :
        self.man.beginClause()
        return self

    def beginAndWhere(self) :
        self.man.beginAndClause()
        return self

    def beginOrWhere(self) :
        self.man.beginOrClause()
        return self

    def beginNotAndWhere(self) :
        self.man.beginNotAndClause()
        return self

    def beginNotOrWhere(self) :
        self.man.beginNotOrClause()
        return self

    def endWhere(self) :
        self.man.endClause(self.man.CLAUSE_WHERE, self.builder)
        return self

    def where(self, column, operator: str, value = None) :
        clauseObject = self.man.andClause(self.man.CLAUSE_WHERE, column, operator, value)
        self.builder.addWhere(clauseObject)
        return self

    def andWhere(self, column, operator: str, value = None) :
        clauseObject = self.man.andClause(self.man.CLAUSE_WHERE, column, operator, value)
        self.builder.addWhere(clauseObject)
        return self

    def orWhere(self, column, operator: str, value = None) :
        clauseObject = self.man.orClause(self.man.CLAUSE_WHERE, column, operator, value)
        self.builder.addWhere(clauseObject)
        return self

    def notAndWhere(self, column, operator: str, value = None) :
        clauseObject = self.man.notAndClause(self.man.CLAUSE_WHERE, column, operator, value)
        self.builder.addWhere(clauseObject)
        return self

    def notOrWhere(self, column, operator: str, value = None) :
        clauseObject = self.man.notOrClause(self.man.CLAUSE_WHERE, column, operator, value)
        self.builder.addWhere(clauseObject)
        return self

    def beginHaving(self) :
        self.man.beginClause()
        return self

    def beginAndHaving(self) :
        self.man.beginAndClause()
        return self

    def beginOrHaving(self) :
        self.man.beginOrClause()
        return self

    def beginNotAndHaving(self) :
        self.man.beginNotAndClause()
        return self

    def beginNotOrHaving(self) :
        self.man.beginNotOrClause()
        return self

    def endHaving(self) :
        self.man.endClause(self.man.CLAUSE_HAVING, self.builder)
        return self

    def having(self, column, operator: str, value = None) :
        clauseObject = self.man.andClause(self.man.CLAUSE_HAVING, column, operator, value)
        self.builder.addHaving(clauseObject)
        return self

    def andHaving(self, column, operator: str, value = None) :
        clauseObject = self.man.andClause(self.man.CLAUSE_HAVING, column, operator, value)
        self.builder.addHaving(clauseObject)
        return self

    def orHaving(self, column, operator: str, value = None) :
        clauseObject = self.man.orClause(self.man.CLAUSE_HAVING, column, operator, value)
        self.builder.addHaving(clauseObject)
        return self

    def notAndHaving(self, column, operator: str, value = None) :
        clauseObject = self.man.notAndClause(self.man.CLAUSE_HAVING, column, operator, value)
        self.builder.addHaving(clauseObject)
        return self

    def notOrHaving(self, column, operator: str, value = None) :
        clauseObject = self.man.notOrClause(self.man.CLAUSE_HAVING, column, operator, value)
        self.builder.addHaving(clauseObject)
        return self

    def groupBy(self, columns) :
        columnObjects = self.man.createGroups(columns)
        for col in columnObjects :
            self.builder.addGroup(col)
        return self

    def orderBy(self, columns, orderType) :
        orderObjects = self.man.createOrders(columns, orderType)
        for order in orderObjects :
            self.builder.addOrder(order)
        return self

    def orderByAsc(self, column) :
        orderObjects = self.man.orderAsc(column)
        for order in orderObjects :
            self.builder.addOrder(order)
        return self

    def orderByDesc(self, column) :
        orderObjects = self.man.orderDesc(column)
        for order in orderObjects :
            self.builder.addOrder(order)
        return self

    def limit(self, limit, offset = None) :
        limitObject = self.man.createLimit(limit, offset)
        self.builder.setLimit(limitObject)
        return self

    def offset(self, offset) :
        limitObject = self.man.offset(offset)
        self.builder.setLimit(limitObject)
        return self
