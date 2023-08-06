from ...Structure import Column
from ...Builder import GroupByBuilder
from typing import Iterable, Mapping

class GroupBy :

    def groupBy(self, columns) :
        columnObjects = ()
        if isinstance(columns, str) :
            columnObjects += (Column.create(columns),)
        elif isinstance(columns, Mapping) :
            for key in columns.keys() :
                columnObjects += (Column.create({key: columns[key]}),)
        elif isinstance(columns, Iterable) :
            for col in columns :
                columnObjects += (Column.create(col),)
        for column in columnObjects :
            if isinstance(self.builder, GroupByBuilder) :
                self.builder.addGroup(column)
            else :
                raise Exception('Builder object does not support GROUP BY query')
        return self
