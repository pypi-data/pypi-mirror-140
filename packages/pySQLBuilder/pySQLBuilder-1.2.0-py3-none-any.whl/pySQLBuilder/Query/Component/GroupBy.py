from ...Structure import Column
from ...Builder import GroupByBuilder

class GroupBy :
    """GROUP BY manipulation component.
    """

    def groupBy(self, columns) :
        """GROUP BY query manipulation"""
        for column in Column.createMulti(columns) :
            if isinstance(self.builder, GroupByBuilder) :
                self.builder.addGroup(column)
            else :
                raise Exception('Builder object does not support GROUP BY query')
        return self
