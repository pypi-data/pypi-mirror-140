from ..QueryObject import QueryObject
from ..Builder import BaseBuilder
from ..Structure import Table, Column, Value, Clause, Order, Limit

class BaseTranslator :

    def __init__(self) :
        self.quote_struct = "`"
        self.quote_string = "'"
        self.equal = "="
        self.open_bracket = "("
        self.close_bracket = ")"
        self.dot = "."
        self.comma = ","
        self.end_query = ""

    def firstKeyword(self, query: QueryObject, builderType: int) :
        if builderType == BaseBuilder.SELECT :
            query.add('SELECT ')
        elif builderType == BaseBuilder.INSERT :
            query.add('INSERT ')
        elif builderType == BaseBuilder.UPDATE :
            query.add('UPDATE ')
        elif builderType == BaseBuilder.DELETE :
            query.add('DELETE')

    def fromTable(self, query: QueryObject, table: Table) :
        name = table.name()
        alias = table.alias()
        query.add(' FROM ' + self.quote_struct)
        query.add(name)
        query.add(self.quote_struct)
        if alias :
            query.add(' AS ' + self.quote_string + alias + self.quote_string)

    def intoTable(self, query: QueryObject, table: Table) :
        name = table.name()
        query.add('INTO ' + self.quote_struct)
        query.add(name)
        query.add(self.quote_struct)

    def tableSet(self, query: QueryObject, table: Table) :
        name = table.name()
        query.add(self.quote_struct)
        query.add(name)
        query.add(self.quote_struct)

    def columnsSelect(self, query: QueryObject, columns: tuple, count: int) :
        if count == 0 :
            query.add('*')
            return
        for column in columns :
            if isinstance(column, Column) :
                name = column.name()
                alias = column.alias()
                function = column.function()
                if function :
                    query.add(function + self.open_bracket)
                query.add(self.quote_struct)
                query.add(name)
                query.add(self.quote_struct)
                if function :
                    query.add(self.close_bracket)
                if alias :
                    query.add(' AS ' + self.quote_string + alias + self.quote_string)
                count -= 1
                if count > 0 : query.add(self.comma)

    def columnsInsert(self, query: QueryObject, values: tuple, count: int) :
        if count == 0 :
            query.add(' ' + self.open_bracket)
            query.add(self.close_bracket)
            return
        value = values[0]
        if isinstance(value, Value) :
            columns = value.columns()
            count = len(columns)
            query.add(' ' + self.open_bracket)
            for column in columns : 
                query.add(self.quote_struct)
                query.add(column)
                query.add(self.quote_struct)
                count -= 1
                if count > 0 : query.add(self.comma)
            query.add(self.close_bracket)

    def column(self, query: QueryObject, column: Column) :
        name = column.name()
        alias = column.alias()
        function = column.function()
        if function :
            query.add(function + self.open_bracket)
        if alias :
            query.add(self.quote_struct)
            query.add(column.alias())
            query.add(self.quote_struct)
        else :
            query.add(self.quote_struct)
            query.add(name)
            query.add(self.quote_struct)
        if function :
            query.add(self.close_bracket)

    def valuesInsert(self, query: QueryObject, values: tuple, count: int) :
        query.add(' VALUES ')
        if count == 0 :
            query.add(self.open_bracket)
            query.add(self.close_bracket)
            return
        for value in values :
            if isinstance(value, Value) :
                vals = value.values()
                countVals = len(vals)
                query.add(self.open_bracket)
                for val in vals :
                    query.add(val, True)
                    countVals -= 1
                    if countVals > 0 : query.add(self.comma)
                query.add(self.close_bracket)
            count -= 1
            if count > 0 : query.add(self.comma)

    def valuesUpdate(self, query: QueryObject, values: tuple, count: int) :
        query.add(' SET ')
        for value in values :
            if isinstance(value, Value) :
                columns = value.columns()
                vals = value.values()
                countVals = len(vals)
                for i, val in enumerate(vals) :
                    query.add(self.quote_struct)
                    query.add(columns[i])
                    query.add(self.quote_struct + self.equal)
                    query.add(val, True)
                    countVals -= 1
                    if countVals > 0 : query.add(self.comma)
            count -= 1
            if count > 1 : query.add(self.comma)

    def operator(self, operator: int) -> str :
        if operator == Clause.OPERATOR_EQUAL :
            return '='
        elif operator == Clause.OPERATOR_NOT_EQUAL :
            return '!='
        elif operator == Clause.OPERATOR_GREATER :
            return '>'
        elif operator == Clause.OPERATOR_GREATER_EQUAL :
            return '>='
        elif operator == Clause.OPERATOR_LESS :
            return '<'
        elif operator == Clause.OPERATOR_LESS_EQUAL :
            return '<='
        elif operator == Clause.OPERATOR_BETWEEN :
            return ' BETWEEN '
        elif operator == Clause.OPERATOR_NOT_BETWEEN :
            return ' NOT BETWEEN '
        elif operator == Clause.OPERATOR_LIKE :
            return ' LIKE '
        elif operator == Clause.OPERATOR_NOT_LIKE :
            return ' NOT LIKE '
        elif operator == Clause.OPERATOR_IN :
            return ' IN '
        elif operator == Clause.OPERATOR_NOT_IN :
            return ' NOT IN '
        elif operator == Clause.OPERATOR_NULL :
            return ' IS NULL '
        elif operator == Clause.OPERATOR_NOT_NULL :
            return ' IS NOT NULL '
        else :
            return ''

    def conjunctive(self, conjunctive: int) -> str :
        if conjunctive == Clause.CONJUNCTIVE_AND :
            return ' AND '
        elif conjunctive == Clause.CONJUNCTIVE_OR :
            return ' OR '
        elif conjunctive == Clause.CONJUNCTIVE_NOT_AND :
            return ' NOT AND '
        elif conjunctive == Clause.CONJUNCTIVE_NOT_OR :
            return ' NOT OR '
        else :
            return ''

    def brackets(self, level: int) -> str :
        string = ''
        if level < 0 :
            for i in range(level, 0) :
                string += self.open_bracket
        elif level > 0 :
            for i in range(0, level) :
                string += self.close_bracket
        return string

    def where(self, query: QueryObject, whereClauses: tuple, count: int) :
        if count :
            query.add(' WHERE ')
            for where in whereClauses :
                if isinstance(where, Clause) :
                    conjunctive = self.conjunctive(where.conjunctive())
                    nestedLevel = where.level()
                    query.add(conjunctive)
                    if nestedLevel < 0 : query.add(self.brackets(nestedLevel))
                    self.clause(query, where)
                    if nestedLevel > 0 : query.add(self.brackets(nestedLevel))

    def having(self, query: QueryObject, havingClauses: tuple, count: int) :
        if count :
            query.add(' HAVING ')
            for having in havingClauses :
                if isinstance(having, Clause) :
                    conjunctive = self.conjunctive(having.conjunctive())
                    nestedLevel = having.level()
                    query.add(conjunctive)
                    if nestedLevel < 0 : query.add(self.brackets(nestedLevel))
                    self.clause(query, having)
                    if nestedLevel > 0 : query.add(self.brackets(nestedLevel))

    def clause(self, query: QueryObject, clause: Clause) :
        column = clause.column()
        operator = clause.operator()
        value = clause.value()
        if isinstance(column, Column) :
            self.column(query, column)
        if operator == Clause.OPERATOR_BETWEEN :
            self.clauseBetween(query, value)
        elif operator == Clause.OPERATOR_IN :
            self.clauseIn(query, value)
        else :
            self.clauseComparison(query, value, operator)

    def clauseComparison(self, query: QueryObject, value, operator: int) :
        query.add(self.operator(operator))
        query.add(value, True)

    def clauseBetween(self, query: QueryObject, value) :
        query.add(self.operator(Clause.OPERATOR_BETWEEN))
        query.add(value[0], True)
        query.add(' AND ')
        query.add(value[1], True)

    def clauseIn(self, query: QueryObject, value) :
        query.add(self.operator(Clause.OPERATOR_IN))
        query.add(self.open_bracket)
        count = len(value)
        for i in range(count) :
            query.add(value[i], True)
            if i < count - 1 : query.add(self.comma)
        query.add(self.close_bracket)

    def groupBy(self, query: QueryObject, groups: tuple, count: int) :
        if count :
            query.add(' GROUP BY ')
            for group in groups :
                if isinstance(group, Column) :
                    self.column(query, group)
                    count -= 1
                    if count > 0 : query.add(self.comma)

    def orderBy(self, query: QueryObject, orders: tuple, count: int) :
        if count :
            query.add(' ORDER BY ')
            for order in orders :
                if isinstance(order, Order) :
                    self.column(query, order.column())
                    if (order.orderType() == Order.ORDER_ASC) :
                        query.add(' ASC')
                    elif (order.orderType() == Order.ORDER_DESC) :
                        query.add(' DESC')
                    count -= 1
                    if count > 0 : query.add(self.comma)

    def limitOffset(self, query: QueryObject, limitOffset: Limit, flag: bool) :
        if flag :
            limit = limitOffset.limit()
            offset = limitOffset.offset()
            if limit == Limit.NOT_SET :
                query.add(' OFFSET ')
                query.add(offset, True)
            else :
                query.add(' LIMIT ')
                query.add(limit, True)
                if offset != Limit.NOT_SET :
                    query.add(self.comma)
                    query.add(offset, True)
