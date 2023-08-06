"""SQL builder library.

Build a query using series of methods. 
Support build query for various RDBMS. 
Can produces a complete query string with input parameters or with separate parameters.

translator option:
- TRANSLATOR_GENERIC
- TRANSLATOR_BEAUTIFY
- TRANSLATOR_MYSQL
- TRANSLATOR_SQLITE

binding option:
- PARAM_NONE
- PARAM_NUM
- PARAM_ASSOC
"""

__version__ = '1.2.0'

from .Constant import *
from .Query import Select, Insert, Update, Delete

translator = TRANSLATOR_GENERIC
binding = PARAM_NUM

table = ''

def select(table_ = None) -> Select :
    """Begin SELECT query builder. Takes a database table as parameter"""
    if table_ is None : table_ = table
    selectQuery = Select(translator, binding)
    return selectQuery.select(table_)

def selectDistinct(table_ = None) -> Select :
    """Begin SELECT DISTINCT query builder. Takes a database table as parameter"""
    if table_ is None : table_ = table
    selectQuery = Select(translator, binding)
    return selectQuery.selectDistinct(table_)

def insert(table_ = None) -> Insert :
    """Begin INSERT query builder. Takes a database table as parameter"""
    if table_ is None : table_ = table
    insertQuery = Insert(translator, binding)
    return insertQuery.insert(table_)

def update(table_ = None) -> Update :
    """Begin UPDATE query builder. Takes a database table as parameter"""
    if table_ is None : table_ = table
    updateQuery = Update(translator, binding)
    return updateQuery.update(table_)

def delete(table_ = None) -> Delete :
    """Begin DELETE query builder. Takes a database table as parameter"""
    if table_ is None : table_ = table
    deleteQuery = Delete(translator, binding)
    return deleteQuery.delete(table_)
