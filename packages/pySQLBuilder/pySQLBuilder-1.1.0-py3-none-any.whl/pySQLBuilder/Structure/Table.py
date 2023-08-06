from typing import Mapping

class Table :

    table = ''

    def __init__(self, name: str, alias: str = '') :
        self.__name = name
        self.__alias = alias

    def name(self) -> str :
        return self.__name

    def alias(self) -> str :
        return self.__alias

    @classmethod
    def create(cls, table) :
        name = ''
        alias = ''
        if isinstance(table, str) :
            cls.table = table
            name = table
            return Table(table)
        elif isinstance(table, Mapping) and len(table) == 1 :
            key = next(iter(table.keys()))
            name = str(table[key])
            alias = str(key)
            cls.table = alias
        return Table(name, alias)
