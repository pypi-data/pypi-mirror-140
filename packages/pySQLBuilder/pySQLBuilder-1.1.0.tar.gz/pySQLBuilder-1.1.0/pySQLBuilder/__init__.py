__version__ = '1.1.0'

from .Constant import *
from .Query import Select, Insert, Update, Delete

translator = TRANSLATOR_GENERIC
bindingOption = PARAM_NUM

table = ''

def select(table_ = None) -> Select :
    if table_ is None : table_ = table
    selectQuery = Select(translator, bindingOption)
    return selectQuery.select(table_)

def insert(table_ = None) -> Insert :
    if table_ is None : table_ = table
    insertQuery = Insert(translator, bindingOption)
    return insertQuery.insert(table_)

def update(table_ = None) -> Update :
    if table_ is None : table_ = table
    updateQuery = Update(translator, bindingOption)
    return updateQuery.update(table_)

def delete(table_ = None) -> Delete :
    if table_ is None : table_ = table
    deleteQuery = Delete(translator, bindingOption)
    return deleteQuery.delete(table_)
