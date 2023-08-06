from .. import QueryTranslator
from ..QueryObject import QueryObject

class BaseQuery :
    """Base of query manipulation class.
    Must be derived for a query manipulation class.
    Contain methods for translating query.
    """

    def __init__(self) :
        self.queryObject = None
        self.builder = None
        self.translator = 0
        self.bindingOption = 0
        self.queryFlag = False
        self.paramFlag = False

    def getQueryObject(self) :
        """Get current state of query object"""
        return self.queryObject

    def getBuilder(self) :
        """Get builder object"""
        return self.builder

    def translate(self, translator: int = 0) :
        """Translate builder object to query object"""
        if translator == 0 : translator = self.translator
        self.queryObject = QueryObject()
        QueryTranslator.translateBuilder(self.queryObject, self.builder, translator)

    def query(self, translator: int = 0, bindingOption: int = 0) :
        """Get query string of current state builder object"""
        if self.queryFlag == self.paramFlag :
            self.translate(translator)
        self.queryFlag = not self.queryFlag
        if bindingOption == 0 : bindingOption = self.bindingOption
        return QueryTranslator.getQuery(self.queryObject, bindingOption)

    def params(self, translator: int = 0, bindingOption: int = 0) :
        """Get query parameters of current state builder object"""
        if self.queryFlag == self.paramFlag :
            self.translate(translator)
        self.paramFlag = not self.paramFlag
        if bindingOption == 0 : bindingOption = self.bindingOption
        return QueryTranslator.getParams(self.queryObject, bindingOption)
