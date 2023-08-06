from ...Structure import Clause
from ...Builder import HavingBuilder

class Having :

    def beginHaving(self) :
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_NONE
        Clause.nestedLevel -= 1
        return self

    def beginAndHaving(self) :
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_AND
        Clause.nestedLevel -= 1
        return self

    def beginOrHaving(self) :
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_OR
        Clause.nestedLevel -= 1
        return self

    def beginNotAndHaving(self) :
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_NOT_AND
        Clause.nestedLevel -= 1
        return self

    def beginNotOrHaving(self) :
        Clause.nestedConjunctive = Clause.CONJUNCTIVE_NOT_OR
        Clause.nestedLevel -= 1
        return self

    def endHaving(self) :
        if isinstance(self.builder, HavingBuilder) :
            lastClause = self.builder.lastHaving()
            if lastClause is not None :
                lastLevel = lastClause.level()
                lastClause.level(lastLevel + 1)
        return self

    def __having(self, column, operator, value, conjunctive: int) :
        clauseObject = Clause.create(Clause.HAVING, column, operator, value, conjunctive)
        if isinstance(self.builder, HavingBuilder) :
            self.builder.addHaving(clauseObject)
        else :
            raise Exception('Builder object does not support HAVING query')
        return self

    def having(self, column, operator: str, value = None) :
        return self.__having(column, operator, value, Clause.CONJUNCTIVE_NONE)

    def andHaving(self, column, operator: str, value = None) :
        return self.__having(column, operator, value, Clause.CONJUNCTIVE_AND)

    def orHaving(self, column, operator: str, value = None) :
        return self.__having(column, operator, value, Clause.CONJUNCTIVE_OR)

    def notAndHaving(self, column, operator: str, value = None) :
        return self.__having(column, operator, value, Clause.CONJUNCTIVE_NOT_AND)

    def notOrHaving(self, column, operator: str, value = None) :
        return self.__having(column, operator, value, Clause.CONJUNCTIVE_NOT_OR)
