from .Constant import *
from .QueryObject import QueryObject
from .Builder import SelectBuilder, InsertBuilder, UpdateBuilder, DeleteBuilder
from .Translator import GenericTranslator, MySQLTranslator

def translateBuilder(query: QueryObject, builder, translator: int) :
    translatorClass = getTranslator(query, translator)
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

def getTranslator(query: QueryObject, translator: int) :
    if translator == TRANSLATOR_GENERIC :
        return GenericTranslator(query)
    elif translator == TRANSLATOR_MYSQL :
        return MySQLTranslator(query)
    else :
        raise Exception('Translator selected is not registered')

def getBindingOption(bindingOption: int) :
    bindingFlag = False
    bindingMode = False
    if bindingOption == PARAM_ASSOC :
        bindingFlag = True
        bindingMode = True
    elif bindingOption == PARAM_NUM :
        bindingFlag = True
        bindingMode = False
    return (bindingFlag, bindingMode)

def getQuery(query: QueryObject, bindingOption: int) -> str :
    (bindingFlag, bindingMode) = getBindingOption(bindingOption)
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

def getParams(query: QueryObject, bindingOption: int) :
    (bindingFlag, bindingMode) = getBindingOption(bindingOption)
    array = None
    if bindingFlag :
        if bindingMode :
            array = {}
            for i, param in enumerate(query.params()) :
                array['v' + str(i)] = param
        else :
            array = query.params()
    return array
