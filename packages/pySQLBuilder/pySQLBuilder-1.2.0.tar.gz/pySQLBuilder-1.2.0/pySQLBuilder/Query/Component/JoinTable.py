from ...Structure import Join
from ...Builder import JoinBuilder
from typing import Iterable

class JoinTable :
    """Join table manipulation component.
    Used for INNER JOIN, LEFT JOIN, RIGHT JOIN, OUTER JOIN query.
    """

    def __init__(self) :
        Join.table = ''

    def join(self, joinTable, joinType) :
        """Add Join object to join property of Builder object"""
        joinObject = Join.create(joinTable, joinType)
        if isinstance(self.builder, JoinBuilder) :
            self.builder.addJoin(joinObject)
        else :
            raise Exception('Builder object does not support JOIN query')
        return self

    def innerJoin(self, joinTable) :
        """INNER JOIN query. Takes join table name input"""
        return self.join(joinTable, Join.INNER_JOIN)

    def leftJoin(self, joinTable) :
        """LEFT JOIN query. Takes join table name input"""
        return self.join(joinTable, Join.LEFT_JOIN)

    def rightJoin(self, joinTable) :
        """RIGHT JOIN query. Takes join table name input"""
        return self.join(joinTable, Join.RIGHT_JOIN)

    def outerJoin(self, joinTable) :
        """OUTER JOIN query. Takes join table name input"""
        return self.join(joinTable, Join.OUTER_JOIN)

    def on(self, baseColumn, joinColumn) :
        """Add join columns and build ON query"""
        if isinstance(self.builder, JoinBuilder) :
            lastJoin = self.builder.lastJoin()
            if lastJoin is not None :
                lastJoin.addColumn(baseColumn, joinColumn)
        return self

    def using(self, columns) :
        """Add join columns and build USING query"""
        if isinstance(columns, str) or not isinstance(columns, Iterable) :
            columns = (columns,)
        if isinstance(self.builder, JoinBuilder) :
            lastJoin = self.builder.lastJoin()
            if lastJoin is not None :
                for column in columns :
                    lastJoin.addColumn(column)
        return self
