from typing import Iterable

class Expression :
    """Object for storing a user custom query expression.
    Object properties:
    - Query expression
    - Expression alias
    - Expression parameters
    """

    def __init__(self, expression: tuple, alias: str = '', params: tuple = ()) :
        countExp = len(expression)
        countPar = len(params)
        if countExp < countPar :
            params = params[:countExp]
        if countExp > countPar :
            for i in range(countPar, countExp) : params += (None,)
        self.__expression = expression
        self.__alias = alias
        self.__params = params

    def expression(self) -> tuple :
        """Get array of expression string."""
        return self.__expression

    def alias(self) -> str :
        """Get alias name of expression."""
        return self.__alias

    def params(self) -> tuple :
        """Get expression parameters array."""
        return self.__params

    @classmethod
    def create(cls, expression, alias = '', params: Iterable = ()) :
        """Create Expression object used in column list, where or having clause column, or group by column."""
        exps = ()
        if isinstance(expression, str) :
            exps = expression.split('?')
        elif isinstance(expression, Iterable) :
            exps = tuple(expression)
        return Expression(exps, str(alias), params)
