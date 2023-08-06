from .QueryObject import QueryObject
from .Query import BaseQuery
from .Builder import SelectBuilder, InsertBuilder, UpdateBuilder, DeleteBuilder
from .Translator import BaseTranslator, GenericTranslator, MySQLTranslator

class QueryTranslator :

    TRANSLATOR_GENERIC = 1
    TRANSLATOR_BEAUTIFY = 2
    TRANSLATOR_MYSQL = 3
    TRANSLATOR_SQLITE = 4

    NO_PARAM = 1
    PARAM_NUM = 2
    PARAM_ASSOC = 3

    def __init__(self, translator: int = TRANSLATOR_GENERIC, bindingOption: int = PARAM_NUM) :
        self.queryObject = QueryObject()
        self.translator = translator
        self.bindingOption = bindingOption

    def getQueryObject(self) :
        return self.queryObject

    def translate(self, queryBuilder: BaseQuery, translator: int = 0, bindingOption: int = 0) -> str :
        if translator == 0: translator = self.translator
        if bindingOption == 0: bindingOption = self.bindingOption
        self.translateBuilder(self.queryObject, queryBuilder.getBuilder(), translator)
        return self.query(bindingOption)

    @staticmethod
    def translateBuilder(query: QueryObject, builder, translator: int) :
        translatorClass = QueryTranslator.getTranslator(query, translator)
        if isinstance(builder, SelectBuilder) :
            translatorClass.translateSelect(query, builder)
        elif isinstance(builder, InsertBuilder) :
            translatorClass.translateInsert(query, builder)
        elif isinstance(builder, UpdateBuilder) :
            translatorClass.translateUpdate(query, builder)
        elif isinstance(builder, DeleteBuilder) :
            translatorClass.translateDelete(query, builder)
        else :
            raise Exception('Tried to translate unregistered builder object')

    @staticmethod
    def getTranslator(query: QueryObject, translator: int) :
        if translator == QueryTranslator.TRANSLATOR_GENERIC :
            return GenericTranslator(query)
        elif translator == QueryTranslator.TRANSLATOR_MYSQL :
            return MySQLTranslator(query)
        else :
            raise Exception('Translator selected is not registered')

    @staticmethod
    def getBindingOption(bindingOption: int) :
        bindingFlag = False
        bindingMode = False
        if bindingOption == QueryTranslator.PARAM_ASSOC :
            bindingFlag = True
            bindingMode = True
        elif bindingOption == QueryTranslator.PARAM_NUM :
            bindingFlag = True
            bindingMode = False
        return (bindingFlag, bindingMode)

    def query(self, bindingOption: int = 0) -> str :
        if bindingOption == 0: bindingOption = self.bindingOption
        return self.getQuery(self.queryObject, bindingOption)

    @staticmethod
    def getQuery(query: QueryObject, bindingOption: int) -> str :
        (bindingFlag, bindingMode) = QueryTranslator.getBindingOption(bindingOption)
        queryString = ''
        parts = query.parts()
        params = query.params()
        if bindingMode : mark = query.bindMarkAssoc()
        else : mark = query.bindMarkNum()
        quote = query.stringQuote()
        for i in range(len(parts)) :
            queryString += parts[i]
            if i < len(params) :
                if bindingFlag :
                    if bindingMode : queryString += (mark + 'v' + str(i))
                    else : queryString += mark
                else :
                    if isinstance(params[i], str) : queryString += (quote + params[i] + quote)
                    else : queryString += str(params[i])
        return queryString

    def params(self, bindingOption: int = 0) :
        if bindingOption == 0: bindingOption = self.bindingOption
        return self.getParams(self.queryObject, bindingOption)

    @staticmethod
    def getParams(query: QueryObject, bindingOption: int) :
        (bindingFlag, bindingMode) = QueryTranslator.getBindingOption(bindingOption)
        array = None
        if bindingFlag :
            if bindingMode :
                array = {}
                for i, param in enumerate(query.params()) :
                    array['v' + str(i)] = param
            else :
                array = query.params()
        return array
