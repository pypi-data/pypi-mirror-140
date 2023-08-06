from ..Builder import Table, Column, Value, Clause, Order, Limit
from typing import Iterable, Mapping

class Manipulation :

    def __init__(self) :
        self.table = ''
        self.clauseType = self.CLAUSE_DEFAULT
        self.nestedConjunctive = Clause.CONJUNCTIVE_NONE
        self.nestedLevel = 0

### TABLE, COLUMN, VALUES QUERY ###

    def createTable(self, table) -> Table :
        name = ''
        alias = ''
        if isinstance(table, str) :
            self.table = table
            name = table
            return Table(table)
        elif isinstance(table, Mapping) and len(table) == 1 :
            key = next(iter(table.keys()))
            name = str(table[key])
            alias = str(key)
            self.table = alias
        return Table(name, alias)

    def createColumn(self, column) -> Column :
        table = ''
        name = ''
        function = ''
        alias = ''
        if isinstance(column, str) :
            (table, name, function) = self.parseColumnStr(column)
        elif isinstance(column, Mapping) :
            (table, name, function, alias) = self.parseColumnMap(column)
        return Column(table, name, function, alias)

    def createColumns(self, columns) -> tuple :
        columnObjects = ()
        if isinstance(columns, Mapping) :
            for key in columns.keys() :
                columnObjects += (self.createColumn({key: columns[key]}),)
        elif isinstance(columns, Iterable) :
            for col in columns :
                columnObjects += (self.createColumn(col),)
        return columnObjects

    def parseColumnStr(self, column: str) -> tuple :
        function = ''
        pos1 = column.find('(')
        pos2 = column.rfind(')')
        if pos1 > 0 and pos2 == len(column) - 1 :
            function = column[0:pos1]
            column = column[pos1+1:pos2]
        table = self.table
        name = self.dequote(column)
        split = column.split('.')
        length = len(split)
        if length == 2 :
            table = self.dequote(split[0])
            name = self.dequote(split[1])
        elif length > 2 :
            pos = column.find('"."')
            if pos <= 0 : pos = column.find("'.'")
            if pos <= 0 : pos = column.find('`.`')
            if pos > 0 :
                table = column[1:pos]
                name = column[pos+3:-1]
        return (table, name, function)

    def parseColumnMap(self, column: Mapping) -> tuple :
        if len(column) == 1 :
            key = next(iter(column.keys()))
            alias = str(key)
            columnStr = str(column[key])
            (table, name, function) = self.parseColumnStr(columnStr)
            return (table, name, function, alias)
        else :
            return ('', '', '', '')

    def createValue(self, inputValue) -> Value :
        columns = ()
        values = ()
        if isinstance(inputValue, Mapping) :
            columns = tuple(inputValue.keys())
            values = tuple(inputValue.values())
        elif isinstance(inputValue, Iterable) :
            (columns, values) = self.parseValuePair(inputValue)
        return Value(self.table, columns, values)

    def createMultiValue(self, multiValues) -> tuple :
        valuesObjects = ()
        if isinstance(multiValues, Iterable) :
            for val in multiValues :
                valuesObjects += (self.createValue(val),)
        return valuesObjects

    def parseValuePair(self, pairs: Iterable) -> tuple :
        if isinstance(pairs[0], str) and len(pairs) == 2 :
            return ((pairs[0],), (pairs[1],))
        columns = ()
        values = ()
        for pair in pairs :
            if isinstance(pair, Mapping) and len(pair) :
                key = next(iter(pair.keys()))
                columns += (key,)
                values += (pair[key],)
            elif isinstance(pair, Iterable) and len(pair) == 2 :
                columns += (pair[0],)
                values += (pair[1],)
        return (columns, values)

    def dequote(self, input: str) -> str :
        if (input[0] == input[-1]) and input.startswith(('"', "'", '`')) :
            return input[1:-1]
        return input

### WHERE AND HAVING CLAUSE QUERY ###

    CLAUSE_DEFAULT = 0
    CLAUSE_WHERE = 1
    CLAUSE_HAVING = 2

    def createClause(self, clauseType: int, column, operator, values, conjunctive: int) -> Clause :
        columnObject = self.createColumn(column)
        validOperator = self.getOperator(operator)
        validValues = self.getValues(values, operator)
        conjunctive = self.getConjunctive(clauseType, conjunctive)
        nestedLevel = self.nestedLevel
        self.clauseType = clauseType
        self.nestedLevel = 0
        return Clause(columnObject, validOperator, validValues, conjunctive, nestedLevel)

    def getOperator(self, operator) -> int :
        if isinstance(operator, int) :
            validOperator = operator
        else :
            if operator == '=' or operator == '==' :
                validOperator = Clause.OPERATOR_EQUAL
            elif operator == '!=' or operator == '<>' :
                validOperator = Clause.OPERATOR_NOT_EQUAL
            elif operator == '>' :
                validOperator = Clause.OPERATOR_GREATER
            elif operator == '>=' :
                validOperator = Clause.OPERATOR_GREATER_EQUAL
            elif operator == '<' :
                validOperator = Clause.OPERATOR_LESS
            elif operator == '<=' :
                validOperator = Clause.OPERATOR_LESS_EQUAL
            elif operator == 'BETWEEN' :
                validOperator = Clause.OPERATOR_BETWEEN
            elif operator == 'NOT BETWEEN' :
                validOperator = Clause.OPERATOR_NOT_BETWEEN
            elif operator == 'LIKE' :
                validOperator = Clause.OPERATOR_LIKE
            elif operator == 'NOT LIKE' :
                validOperator = Clause.OPERATOR_NOT_LIKE
            elif operator == 'IN' :
                validOperator = Clause.OPERATOR_IN
            elif operator == 'NOT IN' :
                validOperator = Clause.OPERATOR_NOT_IN
            elif operator == 'NULL' or operator == 'IS NULL' :
                validOperator = Clause.OPERATOR_NULL
            elif operator == 'NOT NULL' or operator == 'IS NOT NULL' :
                validOperator = Clause.OPERATOR_NOT_NULL
            else :
                validOperator = Clause.OPERATOR_DEFAULT
        return validOperator
            
    def getValues(self, values, operator) :
        valid = True
        if operator == Clause.OPERATOR_BETWEEN or operator == Clause.OPERATOR_NOT_BETWEEN :
            if isinstance(values, Iterable) :
                valid = len(values) == 2
        if operator == Clause.OPERATOR_IN or operator == Clause.OPERATOR_NOT_IN :
            valid = isinstance(values, Iterable)
        if valid :
            return values
        else :
            raise Exception('Invalid input values for Where or Having clause')

    def getConjunctive(self, clauseType: int, conjunctive: int) -> int :
        if clauseType == self.clauseType :
            if conjunctive == Clause.CONJUNCTIVE_NONE :
                if self.nestedConjunctive == Clause.CONJUNCTIVE_NONE : return Clause.CONJUNCTIVE_AND
                else : return self.nestedConjunctive
            else :
                return conjunctive
        else :
            return Clause.CONJUNCTIVE_NONE

    def beginClause(self) :
        self.nestedConjunctive = Clause.CONJUNCTIVE_NONE
        self.nestedLevel -= 1

    def beginAndClause(self) :
        self.nestedConjunctive = Clause.CONJUNCTIVE_AND
        self.nestedLevel -= 1

    def beginOrClause(self) :
        self.nestedConjunctive = Clause.CONJUNCTIVE_OR
        self.nestedLevel -= 1

    def beginNotAndClause(self) :
        self.nestedConjunctive = Clause.CONJUNCTIVE_NOT_AND
        self.nestedLevel -= 1

    def beginNotOrClause(self) :
        self.nestedConjunctive = Clause.CONJUNCTIVE_NOT_OR
        self.nestedLevel -= 1

    def endClause(self, clauseType: int, builder) :
        if clauseType == self.CLAUSE_WHERE :
            lastNested = builder.lastWhere().nestedLevel()
            builder.editWhereNested(lastNested + 1)
        elif clauseType == self.CLAUSE_HAVING :
            lastNested = builder.lastHaving().nestedLevel()
            builder.editHavingNested(lastNested + 1)

    def andClause(self, clauseType: int, column, operator: str, value = None) -> Clause :
        return self.createClause(clauseType, column, operator, value, Clause.CONJUNCTIVE_AND)

    def orClause(self, clauseType: int, column, operator: str, value = None) -> Clause :
        return self.createClause(clauseType, column, operator, value, Clause.CONJUNCTIVE_OR)

    def notAndClause(self, clauseType: int, column, operator: str, value = None) -> Clause :
        return self.createClause(clauseType, column, operator, value, Clause.CONJUNCTIVE_NOT_AND)

    def notOrClause(self, clauseType: int, column, operator: str, value = None) -> Clause :
        return self.createClause(clauseType, column, operator, value, Clause.CONJUNCTIVE_NOT_OR)

### GROUP BY QUERY ###

    def createGroups(self, columns) -> tuple :
        if (isinstance(columns, Mapping) and len(columns) == 1) or isinstance(columns, str) :
            return (self.createColumn(columns),)
        else :
            return self.createColumns(columns)

### ORDER BY QUERY ###

    def createOrders(self, columns, orderType) -> tuple :
        if (isinstance(columns, Mapping) and len(columns) == 1) or isinstance(columns, str) :
            columnObjects = (self.createColumn(columns),)
        else :
            columnObjects = self.createColumns(columns)
        validType = self.getOrderType(orderType)
        orderObjects = ()
        for col in columnObjects :
            orderObjects += (Order(col, validType),)
        return orderObjects

    def getOrderType(self, orderType) -> int :
        if isinstance(orderType, int) :
            validType = orderType
        else :
            if orderType == 'ASCENDING' or orderType == 'ASC' or orderType == 'ascending' or orderType == 'asc' :
                validType = Order.ORDER_ASC
            elif orderType == 'DESCENDING' or orderType == 'DESC' or orderType == 'descending' or orderType == 'desc' :
                validType = Order.ORDER_DESC
            else :
                validType = Order.ORDER_NONE
        return validType

    def orderAsc(self, column) -> Order :
        return self.createOrders(column, Order.ORDER_ASC)

    def orderDesc(self, column) -> Order :
        return self.createOrders(column, Order.ORDER_DESC)

### LIMIT AND OFFSET QUERY ###

    def createLimit(self, limit, offset) -> Limit :
        validLimit = Limit.NOT_SET
        validOffset = Limit.NOT_SET
        if isinstance(limit, int) :
            if limit > 0: validLimit = limit
        if isinstance(offset, int) :
            if offset > 0: validOffset = offset
        return Limit(validLimit, validOffset)

    def offset(self, offset) -> Limit :
        return self.createLimit(Limit.NOT_SET, offset)
