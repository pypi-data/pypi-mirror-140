from .Table import Table
from typing import Iterable, Mapping

class Value :
    """Object for storing a column and value pair of INSERT and UPDATE query.
    Object properties:
    - Table name or alias
    - List of column name
    - List of insert or update value
    """

    def __init__(self, table: str, columns: tuple, values: tuple) :
        self.__table = table
        lenCol = len(columns)
        lenVal = len(values)
        lenMin = lenCol
        if lenCol > lenVal : lenMin = lenVal
        self.__columns = columns[:lenMin]
        self.__values = values[:lenMin]

    def table(self) -> str :
        """Get table name of values"""
        return self.__table

    def columns(self) -> tuple :
        """Get column name of values"""
        return self.__columns

    def values(self) -> tuple :
        """Get values"""
        return self.__values

    @classmethod
    def create(cls, inputValue) :
        """Create Value object from ascossiative array with key as column or sequential array of array."""
        columns = ()
        values = ()
        if isinstance(inputValue, Mapping) :
            for key in inputValue.keys() :
                columns += (cls.getColumn(key),)
            values = tuple(inputValue.values())
        elif isinstance(inputValue, Iterable) :
            (columns, values) = cls.parsePair(inputValue)
        return Value(Table.table, columns, values)

    @classmethod
    def createMulti(cls, inputValues) :
        """Create multiple Value objects."""
        valuesObjects = ()
        if isinstance(inputValues, Iterable) :
            for val in inputValues :
                valuesObjects += (cls.create(val),)
        return valuesObjects

    @classmethod
    def parsePair(cls, pairs: Iterable) -> tuple :
        """Parsing column and value pair from input array."""
        if isinstance(pairs[0], (str, bytes, bytearray)) and len(pairs) == 2 :
            return ((pairs[0],), (pairs[1],))
        columns = ()
        values = ()
        for pair in pairs :
            if isinstance(pair, Mapping) and len(pair) :
                key = next(iter(pair.keys()))
                columns += (cls.getColumn(key),)
                values += (pair[key],)
            elif isinstance(pair, Iterable) and len(pair) == 2 :
                columns += (cls.getColumn(pair[0]),)
                values += (pair[1],)
        return (columns, values)

    @classmethod
    def getColumn(cls, column) -> str :
        validColumn = ''
        if isinstance(column, str) :
            validColumn = column
        elif isinstance(column, (bytes, bytearray)) :
            validColumn = str(column, 'utf-8')
        return validColumn
