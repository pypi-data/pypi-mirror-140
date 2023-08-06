from .Table import Table
from typing import Iterable, Mapping

class Column :
    """Object for storing a column definition.
    Object properties:
    - Table name or alias
    - Column name
    - Column alias
    - Aggregate function
    """

    def __init__(self, table: str, name: str, function: str = '', alias: str = '') :
        self.__table = table
        self.__name = name
        self.__function = function
        self.__alias = alias

    def table(self) -> str :
        """Get table name or table alias of column."""
        return self.__table

    def name(self) -> str :
        """Get name of column."""
        return self.__name

    def function(self) -> str :
        """Get SQL aggregate function."""
        return self.__function

    def alias(self) -> str :
        """Get alias name of column."""
        return self.__alias

    @classmethod
    def create(cls, column) :
        """Create column object from string input or associative array with key as alias."""
        table = ''
        name = ''
        function = ''
        alias = ''
        if isinstance(column, (str, bytes, bytearray)) :
            (table, name, function) = cls.parseStr(column)
        elif isinstance(column, Mapping) :
            (table, name, function, alias) = cls.parseMap(column)
        return Column(table, name, function, alias)

    @classmethod
    def createMulti(cls, columns) :
        """Create multiple Column objects."""
        columnObjects = ()
        if isinstance(columns, (str, bytes, bytearray)) :
            columnObjects = (cls.create(columns),)
        elif isinstance(columns, Mapping) :
            for key in columns.keys() :
                columnObjects += (Column.create({key: columns[key]}),)
        elif isinstance(columns, Iterable) :
            for col in columns :
                columnObjects += (cls.create(col),)
        return columnObjects

    @classmethod
    def parseStr(cls, column) -> tuple :
        """Parsing string input column to table, column name, and aggregate function."""
        if isinstance(column, (bytes, bytearray)) :
            column = str(column, 'utf-8')
        elif not isinstance(column, str) :
            return ('', '', '')
        function = ''
        pos1 = column.find('(')
        pos2 = column.rfind(')')
        if pos1 > 0 and pos2 == len(column) - 1 :
            function = column[0:pos1]
            column = column[pos1+1:pos2]
        table = Table.table
        name = cls.dequote(column)
        split = column.split('.')
        length = len(split)
        if length == 2 :
            table = cls.dequote(split[0])
            name = cls.dequote(split[1])
        elif length > 2 :
            pos = column.find('"."')
            if pos <= 0 : pos = column.find("'.'")
            if pos <= 0 : pos = column.find('`.`')
            if pos > 0 :
                table = column[1:pos]
                name = column[pos+3:-1]
        return (table, name, function)

    @classmethod
    def parseMap(cls, column: Mapping) -> tuple :
        """Parsing array input column to table, column name, aggregate function, and alias name."""
        if len(column) == 1 :
            key = next(iter(column.keys()))
            alias = str(key)
            (table, name, function) = cls.parseStr(column[key])
            return (table, name, function, alias)
        else :
            return ('', '', '', '')

    @classmethod
    def dequote(cls, input: str) -> str :
        if (input[0] == input[-1]) and input.startswith(('"', "'", '`')) :
            return input[1:-1]
        return input
