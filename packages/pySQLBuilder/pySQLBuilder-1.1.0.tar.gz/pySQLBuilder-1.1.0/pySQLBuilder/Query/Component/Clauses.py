from ...Structure import Clause
from ...Builder import WhereBuilder, HavingBuilder

class Clauses :

    def __clauses(self, column, operator: int, value, conjunctive: int) :
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
        return self.__clauses(column, Clause.OPERATOR_EQUAL, value, Clause.CONJUNCTIVE_AND)

    def orEqual(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_EQUAL, value, Clause.CONJUNCTIVE_OR)

    def notEqual(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_NOT_EQUAL, value, Clause.CONJUNCTIVE_AND)

    def notOrEqual(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_NOT_EQUAL, value, Clause.CONJUNCTIVE_OR)

    def greater(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_GREATER, value, Clause.CONJUNCTIVE_AND)

    def orGreater(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_GREATER, value, Clause.CONJUNCTIVE_OR)

    def greaterEqual(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_GREATER_EQUAL, value, Clause.CONJUNCTIVE_AND)

    def orGreaterEqual(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_GREATER_EQUAL, value, Clause.CONJUNCTIVE_OR)

    def less(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_LESS, value, Clause.CONJUNCTIVE_AND)

    def orLess(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_LESS, value, Clause.CONJUNCTIVE_OR)

    def lessEqual(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_LESS_EQUAL, value, Clause.CONJUNCTIVE_AND)

    def orLessEqual(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_LESS_EQUAL, value, Clause.CONJUNCTIVE_OR)

    def between(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_BETWEEN, value, Clause.CONJUNCTIVE_AND)

    def orBetween(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_BETWEEN, value, Clause.CONJUNCTIVE_OR)

    def notBetween(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_NOT_BETWEEN, value, Clause.CONJUNCTIVE_AND)

    def notOrBetween(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_NOT_BETWEEN, value, Clause.CONJUNCTIVE_OR)

    def In(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_IN, value, Clause.CONJUNCTIVE_AND)

    def orIn(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_IN, value, Clause.CONJUNCTIVE_OR)

    def notIn(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_NOT_IN, value, Clause.CONJUNCTIVE_AND)

    def notOrIn(self, column, value) :
        return self.__clauses(column, Clause.OPERATOR_NOT_IN, value, Clause.CONJUNCTIVE_OR)

    def isNull(self, column) :
        return self.__clauses(column, Clause.OPERATOR_NULL, None, Clause.CONJUNCTIVE_AND)

    def orIsNull(self, column) :
        return self.__clauses(column, Clause.OPERATOR_NULL, None, Clause.CONJUNCTIVE_OR)

    def notIsNull(self, column) :
        return self.__clauses(column, Clause.OPERATOR_NOT_NULL, None, Clause.CONJUNCTIVE_AND)

    def notOrIsNull(self, column) :
        return self.__clauses(column, Clause.OPERATOR_NOT_NULL, None, Clause.CONJUNCTIVE_OR)
