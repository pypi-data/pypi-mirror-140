from ...Structure import Clause, Expression
from ...Builder import HavingBuilder
from typing import Iterable

class Having :
    """HAVING clause manipulation component.
    Used for HAVING query.
    """

    def beginHaving(self) :
        """Begin a nested HAVING clause"""
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_NONE
        Clause.nestedLevel -= 1
        return self

    def beginAndHaving(self) :
        """Begin a nested HAVING clause with AND conjunctive"""
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_AND
        Clause.nestedLevel -= 1
        return self

    def beginOrHaving(self) :
        """Begin a nested HAVING clause with OR conjunctive"""
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_OR
        Clause.nestedLevel -= 1
        return self

    def beginNotAndHaving(self) :
        """Begin a nested HAVING clause with NOT AND conjunctive"""
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_NOT_AND
        Clause.nestedLevel -= 1
        return self

    def beginNotOrHaving(self) :
        """Begin a nested HAVING clause with NOT OR conjunctive"""
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_NOT_OR
        Clause.nestedLevel -= 1
        return self

    def endHaving(self) :
        """End a nested HAVING clause"""
        if isinstance(self.builder, HavingBuilder) :
            lastClause = self.builder.lastHaving()
            if lastClause is not None :
                lastLevel = lastClause.level()
                lastClause.level(lastLevel + 1)
        return self

    def __having(self, column, operator, value, conjunctive: int) :
        """Add Clause object to having property of Builder object"""
        clauseObject = Clause.create(Clause.HAVING, column, operator, value, conjunctive)
        if isinstance(self.builder, HavingBuilder) :
            self.builder.addHaving(clauseObject)
        else :
            raise Exception('Builder object does not support HAVING query')
        return self

    def having(self, column, operator: str, value = None) :
        """HAVING query without conjunctive"""
        return self.__having(column, operator, value, Clause.CONJUNCTIVE_NONE)

    def andHaving(self, column, operator: str, value = None) :
        """HAVING query with AND conjunctive"""
        return self.__having(column, operator, value, Clause.CONJUNCTIVE_AND)

    def orHaving(self, column, operator: str, value = None) :
        """HAVING query with OR conjunctive"""
        return self.__having(column, operator, value, Clause.CONJUNCTIVE_OR)

    def notAndHaving(self, column, operator: str, value = None) :
        """HAVING query with NOT AND conjunctive"""
        return self.__having(column, operator, value, Clause.CONJUNCTIVE_NOT_AND)

    def notOrHaving(self, column, operator: str, value = None) :
        """HAVING query with NOT OR conjunctive"""
        return self.__having(column, operator, value, Clause.CONJUNCTIVE_NOT_OR)

    def havingExpression(self, expression, operator, value, params: Iterable = ()) :
        """HAVING expression query with AND conjunctive"""
        expressionObject = Expression.create(expression, '', params)
        return self.__having(expressionObject, operator, value, Clause.CONJUNCTIVE_AND)

    def orHavingExpression(self, expression, operator, value, params: Iterable = ()) :
        """HAVING expression query with OR conjunctive"""
        expressionObject = Expression.create(expression, '', params)
        return self.__having(expressionObject, operator, value, Clause.CONJUNCTIVE_OR)

    def notHavingExpression(self, expression, operator, value, params: Iterable = ()) :
        """HAVING expression query with NOT AND conjunctive"""
        expressionObject = Expression.create(expression, '', params)
        return self.__having(expressionObject, operator, value, Clause.CONJUNCTIVE_NOT_AND)

    def notOrHavingExpression(self, expression, operator, value, params: Iterable = ()) :
        """HAVING expression query with NOT OR conjunctive"""
        expressionObject = Expression.create(expression, '', params)
        return self.__having(expressionObject, operator, value, Clause.CONJUNCTIVE_NOT_OR)
