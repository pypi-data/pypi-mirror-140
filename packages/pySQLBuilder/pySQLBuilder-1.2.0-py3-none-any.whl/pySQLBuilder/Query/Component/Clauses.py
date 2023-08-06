from ...Structure import Clause
from ...Builder import WhereBuilder, HavingBuilder

class Clauses :
    """Clause manipulation component.
    Used for WHERE and HAVING query.
    """

    def __init__(self) :
        Clause.clauseType = Clause.NONE
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_NONE
        Clause.nestedLevel = 0

    def __clauses(self, column, operator: int, value, conjunctive: int) :
        """Add Clause object to where or having property of builder object"""
        clauseType = Clause.clauseType
        if clauseType == Clause.NONE : clauseType = Clause.WHERE
        clauseObject = Clause.create(clauseType, column, operator, value, conjunctive)
        if isinstance(self.builder, WhereBuilder) or isinstance(self.builder, HavingBuilder) :
            if Clause.clauseType == Clause.HAVING :
                self.builder.addHaving(clauseObject)
            else :
                self.builder.addWhere(clauseObject)
        else :
            raise Exception('Builder object does not support WHERE or HAVING query')
        return self

    def equal(self, column, value) :
        """WHERE or HAVING clause query with "=" operator and AND conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_EQUAL, value, Clause.CONJUNCTIVE_AND)

    def orEqual(self, column, value) :
        """WHERE or HAVING clause query with "=" operator and OR conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_EQUAL, value, Clause.CONJUNCTIVE_OR)

    def notEqual(self, column, value) :
        """WHERE or HAVING clause query with "!=" operator and AND conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_NOT_EQUAL, value, Clause.CONJUNCTIVE_AND)

    def notOrEqual(self, column, value) :
        """WHERE or HAVING clause query with "!=" operator and OR conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_NOT_EQUAL, value, Clause.CONJUNCTIVE_OR)

    def greater(self, column, value) :
        """WHERE or HAVING clause query with ">" operator and AND conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_GREATER, value, Clause.CONJUNCTIVE_AND)

    def orGreater(self, column, value) :
        """WHERE or HAVING clause query with ">" operator and OR conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_GREATER, value, Clause.CONJUNCTIVE_OR)

    def greaterEqual(self, column, value) :
        """WHERE or HAVING clause query with ">=" operator and AND conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_GREATER_EQUAL, value, Clause.CONJUNCTIVE_AND)

    def orGreaterEqual(self, column, value) :
        """WHERE or HAVING clause query with ">=" operator and OR conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_GREATER_EQUAL, value, Clause.CONJUNCTIVE_OR)

    def less(self, column, value) :
        """WHERE or HAVING clause query with "<" operator and AND conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_LESS, value, Clause.CONJUNCTIVE_AND)

    def orLess(self, column, value) :
        """WHERE or HAVING clause query with "<" operator and OR conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_LESS, value, Clause.CONJUNCTIVE_OR)

    def lessEqual(self, column, value) :
        """WHERE or HAVING clause query with "<=" operator and AND conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_LESS_EQUAL, value, Clause.CONJUNCTIVE_AND)

    def orLessEqual(self, column, value) :
        """WHERE or HAVING clause query with "<=" operator and OR conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_LESS_EQUAL, value, Clause.CONJUNCTIVE_OR)

    def between(self, column, value) :
        """WHERE or HAVING clause query with BETWEEN operator and AND conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_BETWEEN, value, Clause.CONJUNCTIVE_AND)

    def orBetween(self, column, value) :
        """WHERE or HAVING clause query with BETWEEN operator and OR conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_BETWEEN, value, Clause.CONJUNCTIVE_OR)

    def notBetween(self, column, value) :
        """WHERE or HAVING clause query with NOT BETWEEN operator and AND conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_NOT_BETWEEN, value, Clause.CONJUNCTIVE_AND)

    def notOrBetween(self, column, value) :
        """WHERE or HAVING clause query with NOT BETWEEN operator and OR conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_NOT_BETWEEN, value, Clause.CONJUNCTIVE_OR)

    def In(self, column, value) :
        """WHERE or HAVING clause query with IN operator and AND conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_IN, value, Clause.CONJUNCTIVE_AND)

    def orIn(self, column, value) :
        """WHERE or HAVING clause query with IN operator and OR conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_IN, value, Clause.CONJUNCTIVE_OR)

    def notIn(self, column, value) :
        """WHERE or HAVING clause query with NOT IN operator and AND conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_NOT_IN, value, Clause.CONJUNCTIVE_AND)

    def notOrIn(self, column, value) :
        """WHERE or HAVING clause query with NOT IN operator and OR conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_NOT_IN, value, Clause.CONJUNCTIVE_OR)

    def isNull(self, column) :
        """WHERE or HAVING clause query with NULL operator and AND conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_NULL, None, Clause.CONJUNCTIVE_AND)

    def orIsNull(self, column) :
        """WHERE or HAVING clause query with NULL operator and OR conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_NULL, None, Clause.CONJUNCTIVE_OR)

    def notIsNull(self, column) :
        """WHERE or HAVING clause query with NOT NULL operator and AND conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_NOT_NULL, None, Clause.CONJUNCTIVE_AND)

    def notOrIsNull(self, column) :
        """WHERE or HAVING clause query with NOT NULL operator and OR conjunctive"""
        return self.__clauses(column, Clause.OPERATOR_NOT_NULL, None, Clause.CONJUNCTIVE_OR)
