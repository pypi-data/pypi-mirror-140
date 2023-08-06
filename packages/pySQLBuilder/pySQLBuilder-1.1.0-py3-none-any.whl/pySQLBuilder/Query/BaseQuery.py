from .. import QueryTranslator
from ..QueryObject import QueryObject

class BaseQuery :

    def __init__(self) :
        self.queryObject = None
        self.builder = None
        self.translator = 0
        self.bindingOption = 0
        self.translateFlag = True

    def getQueryObject(self) :
        return self.queryObject

    def getBuilder(self) :
        return self.builder

    def translate(self, translator: int = 0) :
        if translator == 0 : translator = self.translator
        self.queryObject = QueryObject()
        QueryTranslator.translateBuilder(self.queryObject, self.builder, translator)

    def query(self, translator: int = 0, bindingOption: int = 0) :
        if self.translateFlag :
            self.translate(translator)
            self.translateFlag = False
        if bindingOption == 0 : bindingOption = self.bindingOption
        return QueryTranslator.getQuery(self.queryObject, bindingOption)

    def params(self, translator: int = 0, bindingOption: int = 0) :
        if self.translateFlag :
            self.translate(translator)
            self.translateFlag = False
        if bindingOption == 0 : bindingOption = self.bindingOption
        return QueryTranslator.getParams(self.queryObject, bindingOption)
