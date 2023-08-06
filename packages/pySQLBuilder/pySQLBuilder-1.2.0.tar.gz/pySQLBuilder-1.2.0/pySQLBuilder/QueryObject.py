class QueryObject :
    """An object for storing translated query.
    Contain list of query string parts and query parameters
    """

    def __init__(self) :
        """Clear query parts and all parameters"""
        self.__parts = ()
        self.__params = ()
        self.__number = -1
        self.__paramSet = True
        self.__bindMarkNum = '?'
        self.__bindMarkAssoc = ':'
        self.__stringQuote = '\''

    def parts(self) -> tuple :
        """Get query parts list"""
        return self.__parts

    def params(self) -> tuple :
        """Get value parameters list"""
        return self.__params

    def add(self, queryPart, paramFlag: bool = False) :
        """Add a query part or a query parameter to the list"""
        if not paramFlag or self.__number < 0 :
            if self.__paramSet :
                self.__parts += (queryPart,)
                self.__paramSet = False
                self.__number += 1
            else :
                self.__parts = self.__parts[:self.__number] + (self.__parts[self.__number] + queryPart,)
        else :
            self.__params += (queryPart,)
            self.__paramSet = True

    def bindMarkNum(self) -> str :
        """Get sequential binding mark"""
        return self.__bindMarkNum

    def bindMarkAssoc(self) -> str :
        """Get associative binding mark"""
        return self.__bindMarkAssoc

    def stringQuote(self) -> str :
        """Get string value quote character"""
        return self.__stringQuote

    def setMarkQuote(self, bindMarkNum: str, bindMarkAssoc: str, stringQuote: str) :
        """Set sequential and associative binding mark and quote character"""
        self.__bindMarkNum = bindMarkNum
        self.__bindMarkAssoc = bindMarkAssoc
        self.__stringQuote = stringQuote
