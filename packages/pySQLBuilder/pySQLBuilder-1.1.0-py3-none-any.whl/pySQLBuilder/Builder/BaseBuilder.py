from ..Structure import Table, Column, Value

class BaseBuilder :

    SELECT = 1
    INSERT = 2
    UPDATE = 3
    DELETE = 4
    SELECT_DISTINCT = 5
    SELECT_UNION = 6
    SELECT_INTERSECT = 7
    SELECT_MINUS = 8
    INSERT_COPY = 9

    def __init__(self) :
        self.__builderType = 0
        self.__table = None
        self.__columns = ()
        self.__values = ()

    def builderType(self, type: int = 0) -> int :
        if (type > 0 and type <= 9) :
            self.__builderType = type
        return self.__builderType

    def getTable(self) -> Table :
        return self.__table

    def setTable(self, table: Table) :
        self.__table = table

    def getColumns(self) -> tuple :
        return self.__columns

    def countColumns(self) -> int :
        return len(self.__columns)

    def addColumn(self, column) :
        if isinstance(column, Column) :
            self.__columns = self.__columns + (column,)

    def getValues(self) -> tuple :
        return self.__values

    def countValues(self) -> int :
        return len(self.__values)

    def addValue(self, value : Value) :
        self.__values = self.__values + (value,)
