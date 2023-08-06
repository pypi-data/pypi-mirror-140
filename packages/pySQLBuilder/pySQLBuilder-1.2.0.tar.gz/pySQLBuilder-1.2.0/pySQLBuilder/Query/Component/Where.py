from ...Structure import Clause, Expression
from ...Builder import WhereBuilder
from typing import Iterable

class Where :
    """WHERE clause manipulation component.
    Used for WHERE query.
    """

    def beginWhere(self) :
        """Begin a nested WHERE clause"""
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_NONE
        Clause.nestedLevel -= 1
        return self

    def beginAndWhere(self) :
        """Begin a nested WHERE clause with AND conjunctive"""
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_AND
        Clause.nestedLevel -= 1
        return self

    def beginOrWhere(self) :
        """Begin a nested WHERE clause with OR conjunctive"""
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_OR
        Clause.nestedLevel -= 1
        return self

    def beginNotAndWhere(self) :
        """Begin a nested WHERE clause with NOT AND conjunctive"""
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_NOT_AND
        Clause.nestedLevel -= 1
        return self

    def beginNotOrWhere(self) :
        """Begin a nested WHERE clause with NOT OR conjunctive"""
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_NOT_OR
        Clause.nestedLevel -= 1
        return self

    def endWhere(self) :
        """End a nested WHERE clause"""
        if isinstance(self.builder, WhereBuilder) :
            lastClause = self.builder.lastWhere()
            if lastClause is not None :
                lastLevel = lastClause.level()
                lastClause.level(lastLevel + 1)
        return self

    def __where(self, column, operator, value, conjunctive: int) :
        """Add Clause object to where property of Builder object"""
        clauseObject = Clause.create(Clause.WHERE, column, operator, value, conjunctive)
        if isinstance(self.builder, WhereBuilder) :
            self.builder.addWhere(clauseObject)
        else :
            raise Exception('Builder object does not support WHERE query')
        return self

    def where(self, column, operator, value = None) :
        """WHERE query without conjunctive"""
        return self.__where(column, operator, value, Clause.CONJUNCTIVE_NONE)

    def andWhere(self, column, operator, value = None) :
        """WHERE query with AND conjunctive"""
        return self.__where(column, operator, value, Clause.CONJUNCTIVE_AND)

    def orWhere(self, column, operator, value = None) :
        """WHERE query with OR conjunctive"""
        return self.__where(column, operator, value, Clause.CONJUNCTIVE_OR)

    def notAndWhere(self, column, operator, value = None) :
        """WHERE query with NOT AND conjunctive"""
        return self.__where(column, operator, value, Clause.CONJUNCTIVE_NOT_AND)

    def notOrWhere(self, column, operator, value = None) :
        """WHERE query with NOT OR conjunctive"""
        return self.__where(column, operator, value, Clause.CONJUNCTIVE_NOT_OR)

    def whereExpression(self, expression, operator, value, params: Iterable = ()) :
        """WHERE expression query with AND conjunctive"""
        expressionObject = Expression.create(expression, '', params)
        return self.__where(expressionObject, operator, value, Clause.CONJUNCTIVE_AND)

    def orWhereExpression(self, expression, operator, value, params: Iterable = ()) :
        """WHERE expression query with OR conjunctive"""
        expressionObject = Expression.create(expression, '', params)
        return self.__where(expressionObject, operator, value, Clause.CONJUNCTIVE_OR)

    def notWhereExpression(self, expression, operator, value, params: Iterable = ()) :
        """WHERE expression query with NOT AND conjunctive"""
        expressionObject = Expression.create(expression, '', params)
        return self.__where(expressionObject, operator, value, Clause.CONJUNCTIVE_NOT_AND)

    def notOrWhereExpression(self, expression, operator, value, params: Iterable = ()) :
        """WHERE expression query with NOT OR conjunctive"""
        expressionObject = Expression.create(expression, '', params)
        return self.__where(expressionObject, operator, value, Clause.CONJUNCTIVE_NOT_OR)
