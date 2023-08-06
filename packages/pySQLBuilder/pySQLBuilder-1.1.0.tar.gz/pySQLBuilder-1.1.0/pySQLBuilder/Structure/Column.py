from .Table import Table
from typing import Mapping

class Column :

    def __init__(self, table: str, name: str, function: str = '', alias: str = '') :
        self.__table = table
        self.__name = name
        self.__function = function
        self.__alias = alias

    def table(self) -> str :
        return self.__table

    def name(self) -> str :
        return self.__name

    def function(self) -> str :
        return self.__function

    def alias(self) -> str :
        return self.__alias

    @classmethod
    def create(cls, column) :
        table = ''
        name = ''
        function = ''
        alias = ''
        if isinstance(column, str) :
            (table, name, function) = cls.parseStr(column)
        elif isinstance(column, Mapping) :
            (table, name, function, alias) = cls.parseMap(column)
        return Column(table, name, function, alias)

    @classmethod
    def parseStr(cls, column: str) -> tuple :
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
        if len(column) == 1 :
            key = next(iter(column.keys()))
            alias = str(key)
            columnStr = str(column[key])
            (table, name, function) = cls.parseStr(columnStr)
            return (table, name, function, alias)
        else :
            return ('', '', '', '')

    @classmethod
    def dequote(cls, input: str) -> str :
        if (input[0] == input[-1]) and input.startswith(('"', "'", '`')) :
            return input[1:-1]
        return input
