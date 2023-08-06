from ..QueryObject import QueryObject
from ..QueryTranslator import QueryTranslator
from ..Builder import BaseBuilder

class BaseQuery :

    builder = BaseBuilder()
    queryObject = QueryObject()

    options = (QueryTranslator.TRANSLATOR_GENERIC, QueryTranslator.PARAM_NUM)
    statement = None
    translateFlag = True

    def getQueryObject(self) :
        return self.queryObject

    def getBuilder(self) :
        return self.builder

    def translate(self, translator: int = 0) :
        if translator == 0 : translator = self.options[0]
        self.queryObject = QueryObject()
        QueryTranslator.translateBuilder(self.queryObject, self.builder, translator)

    def query(self, translator: int = 0, bindingOption: int = 0) :
        if self.translateFlag :
            self.translate(translator)
            self.translateFlag = False
        if bindingOption == 0 : bindingOption = self.options[1]
        return QueryTranslator.getQuery(self.queryObject, bindingOption)

    def params(self, translator: int = 0, bindingOption: int = 0) :
        if self.translateFlag :
            self.translate(translator)
            self.translateFlag = False
        if bindingOption == 0 : bindingOption = self.options[1]
        return QueryTranslator.getParams(self.queryObject, bindingOption)
