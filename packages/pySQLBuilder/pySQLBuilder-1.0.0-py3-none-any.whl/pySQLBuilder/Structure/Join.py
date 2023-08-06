from .Table import Table
from .Column import Column
from typing import Mapping

class Join :
    """Object for storing join table query definition. Used in INNER JOIN, LEFT JOIN, RIGHT JOIN, or OUTER JOIN query
    Object properties:
    - Join type
    - Base table name
    - Join table name
    - Join table alias name
    - List of base column objects
    - List of join column objects
    - List of using column objects
    """

    NO_JOIN = 0
    INNER_JOIN = 1
    LEFT_JOIN = 2
    RIGHT_JOIN = 3
    OUTER_JOIN = 4

    table = ''

    def __init__(self, joinType: int, baseTable: str, joinTable: str, joinAlias: str = '') :
        self.__joinType = joinType
        self.__baseTable = baseTable
        self.__joinTable = joinTable
        self.__joinAlias = joinAlias
        self.__baseColumns = ()
        self.__joinColumns = ()
        self.__usingColumns = ()

    def joinType(self) -> int :
        """Get join type."""
        return self.__joinType

    def baseTable(self) -> str :
        """Get base table name."""
        return self.__baseTable

    def joinTable(self) -> str :
        """Get join table name."""
        return self.__joinTable

    def joinAlias(self) -> str :
        """Get join table alias name."""
        return self.__joinAlias

    def baseColumns(self) -> tuple :
        """Get base column objects list."""
        return self.__baseColumns

    def joinColumns(self) -> tuple :
        """Get join column objects list"""
        return self.__joinColumns

    def usingColumns(self) -> tuple :
        """Get using column objects list"""
        return self.__usingColumns

    @classmethod
    def create(cls, joinTable, joinType) :
        """Create join table object from joint type and input table"""
        cls.table = Table.table
        validType = cls.getType(joinType)
        if isinstance(joinTable, Mapping) :
            key = next(iter(joinTable.keys()))
            joinAlias = str(key)
            joinObject = Join(validType, Table.table, cls.getTable(joinTable[key]), joinAlias)
            Table.table = joinAlias
        else :
            joinTable = cls.getTable(joinTable)
            joinObject = Join(validType, Table.table, joinTable)
            Table.table = joinTable
        return joinObject

    @classmethod
    def getType(cls, joinType) -> int :
        """Get a valid join type option from input join type."""
        if isinstance(joinType, int) :
            validType = joinType
            if joinType < 0 or joinType > 4 : validType = 0
        else :
            if joinType == 'INNER JOIN' or joinType == 'INNER' :
                validType = Join.INNER_JOIN
            elif joinType == 'LEFT JOIN' or joinType == 'LEFT' :
                validType = Join.LEFT_JOIN
            elif joinType == 'RIGHT JOIN' or joinType == 'RIGHT' :
                validType = Join.RIGHT_JOIN
            elif joinType == 'OUTER JOIN' or joinType == 'OUTER' :
                validType = Join.OUTER_JOIN
            else :
                validType = Join.NO_JOIN
        return validType

    @classmethod
    def getTable(cls, table) -> str :
        valiTable = ''
        if isinstance(table, str) :
            valiTable += table
        elif isinstance(table, bytes) or isinstance(table, bytearray) :
            valiTable += str(table, 'utf-8')
        return valiTable

    def addColumn(self, baseColumn, joinColumn = None) :
        """Add columns object property to a join table object."""
        table = Table.table
        Table.table = Join.table
        baseColumnObject = Column.create(baseColumn)
        Table.table = table
        if joinColumn is None :
            self.__usingColumns += (baseColumnObject,)
        else :
            joinColumnObject = Column.create(joinColumn)
            self.__baseColumns += (baseColumnObject,)
            self.__joinColumns += (joinColumnObject,)
