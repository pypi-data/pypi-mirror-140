from .Column import Column
from .Expression import Expression
from typing import Iterable

class Clause :
    """Object for storing a clause query structure. Used in WHERE and HAVING query.
    Object properties:
    - Column or Expression object
    - Clause operator
    - Clause comparison value
    - Clause conjunctive
    - Nested level
    """

    NONE = 0
    WHERE = 1
    HAVING = 2

    OPERATOR_DEFAULT = 0
    OPERATOR_EQUAL = 1
    OPERATOR_NOT_EQUAL = 2
    OPERATOR_GREATER = 3
    OPERATOR_GREATER_EQUAL = 4
    OPERATOR_LESS = 5
    OPERATOR_LESS_EQUAL = 6
    OPERATOR_LIKE = 7
    OPERATOR_NOT_LIKE = 8
    OPERATOR_BETWEEN = 9
    OPERATOR_NOT_BETWEEN = 10
    OPERATOR_IN = 11
    OPERATOR_NOT_IN = 12
    OPERATOR_NULL = 13
    OPERATOR_NOT_NULL = 14

    CONJUNCTIVE_NONE = 0
    CONJUNCTIVE_AND = 1
    CONJUNCTIVE_OR = 2
    CONJUNCTIVE_NOT_AND = 3
    CONJUNCTIVE_NOT_OR = 4

    clauseType = NONE
    nestedConjunctive = CONJUNCTIVE_NONE
    nestedLevel = 0

    def __init__(self, column, operator: int, value, conjunctive: int, level: int) :
        self.__column = column
        if operator > 0 and operator <= 14 :
            self.__operator = operator
        else :
            self.__operator = self.OPERATOR_DEFAULT
        self.__value = value
        if conjunctive > 0 and conjunctive <= 4 :
            self.__conjunctive = conjunctive
        else :
            self.__conjunctive = self.CONJUNCTIVE_NONE
        self.__level = level

    def column(self) :
        """Get clause column. Can be column object or expression object."""
        return self.__column

    def operator(self) -> int :
        """Get operator type."""
        return self.__operator

    def value(self) :
        """Get clause comparison value."""
        return self.__value

    def conjunctive(self) -> int :
        """Get clause conjunctive type."""
        return self.__conjunctive

    def level(self, input: int = -1) -> int :
        """Get or set nested clause level. Negative for open parenthesis and positive for close parenthesis."""
        if input > -1 : self.__level = input
        return self.__level

    @classmethod
    def create(cls, clauseType: int, column, operator, value, conjunctive: int) :
        """Create Clause object from column input, operator, value, and conjunctive for WHERE or HAVING query."""
        if isinstance(column, (Expression, Column)) :
            columnObject = column
        else :
            columnObject = Column.create(column)
        validOperator = cls.getOperator(operator)
        validValue = cls.getValue(value, validOperator)
        conjunctive = cls.getConjunctive(clauseType, conjunctive)
        nestedLevel = cls.nestedLevel
        cls.clauseType = clauseType
        cls.nestedLevel = 0
        return Clause(columnObject, validOperator, validValue, conjunctive, nestedLevel)

    @classmethod
    def getOperator(cls, operator) -> int :
        """Get a valid operator option from input operator."""
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

    @classmethod
    def getValue(cls, value, operator: int) :
        """Check and get valid clause comparison value."""
        valid = True
        if operator == Clause.OPERATOR_BETWEEN or operator == Clause.OPERATOR_NOT_BETWEEN :
            if isinstance(value, Iterable) :
                valid = len(value) == 2
        if operator == Clause.OPERATOR_IN or operator == Clause.OPERATOR_NOT_IN :
            valid = isinstance(value, Iterable)
        if valid :
            return value
        else :
            raise Exception('Invalid input value for Where or Having clause')

    @classmethod
    def getConjunctive(cls, clauseType: int, conjunctive: int) -> int :
        """Get appropriate conjunctive from input conjunctive."""
        if clauseType == cls.clauseType :
            if conjunctive == Clause.CONJUNCTIVE_NONE :
                if cls.nestedConjunctive == Clause.CONJUNCTIVE_NONE : return Clause.CONJUNCTIVE_AND
                else : return cls.nestedConjunctive
            else :
                return conjunctive
        else :
            return Clause.CONJUNCTIVE_NONE
