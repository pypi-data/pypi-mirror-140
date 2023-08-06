from typing import Mapping

class Table :
    """Object for storing a table definition.
    Object properties:
    - Table name
    - Table name alias
    """

    table = ''

    def __init__(self, name: str, alias: str = '') :
        self.__name = name
        self.__alias = alias

    def name(self) -> str :
        """Get table name."""
        return self.__name

    def alias(self) -> str :
        """Get table alias."""
        return self.__alias

    @classmethod
    def create(cls, table) :
        """Create table object from string input or ascossiative array with key as alias."""
        name = ''
        alias = ''
        if isinstance(table, str) :
            name = table
            cls.table = table
        elif isinstance(table, bytes) or isinstance(table, bytearray) :
            name = str(table, 'utf-8')
            cls.table = name
        elif isinstance(table, Mapping) and len(table) == 1 :
            key = next(iter(table.keys()))
            name = str(table[key])
            alias = str(key)
            cls.table = alias
        return Table(name, alias)
