from ..Structure import Table, Column, Value, Expression

class BaseBuilder :
    """Base of builder object.
    Basic template for building a query
    """

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
        """Get or set builder object type"""
        if (type > 0 and type <= 9) :
            self.__builderType = type
        return self.__builderType

    def getTable(self) -> Table :
        """Get table of a builder"""
        return self.__table

    def setTable(self, table: Table) :
        """Set table for a builder"""
        self.__table = table

    def getColumns(self) -> tuple :
        """Get list of columns"""
        return self.__columns

    def countColumns(self) -> int :
        """Count column list"""
        return len(self.__columns)

    def addColumn(self, column) :
        """Add a column or column expression to Column list"""
        if isinstance(column, Column) or isinstance(column, Expression) :
            self.__columns = self.__columns + (column,)

    def getValues(self) -> tuple :
        """Get Value list"""
        return self.__values

    def countValues(self) -> int :
        """Count Value list"""
        return len(self.__values)

    def addValue(self, value : Value) :
        """Add a value to Value list"""
        self.__values = self.__values + (value,)
