class QueryObject :

    def __init__(self) :
        self.__parts = ()
        self.__params = ()
        self.__number = -1
        self.__paramSet = True
        self.__bindMarkNum = '?'
        self.__bindMarkAssoc = ':'
        self.__stringQuote = '\''

    def parts(self) -> tuple :
        return self.__parts

    def params(self) -> tuple :
        return self.__params

    def add(self, queryPart, paramFlag: bool = False) :
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
        return self.__bindMarkNum

    def bindMarkAssoc(self) -> str :
        return self.__bindMarkAssoc

    def stringQuote(self) -> str :
        return self.__stringQuote

    def setMarkQuote(self, bindMarkNum: str, bindMarkAssoc: str, stringQuote: str) :
        self.__bindMarkNum = bindMarkNum
        self.__bindMarkAssoc = bindMarkAssoc
        self.__stringQuote = stringQuote
