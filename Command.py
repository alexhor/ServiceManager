#!/usr/bin/python3

from ast import literal_eval
from typing import Any, Type


class Command:
    _argList: list
    _commandString: str

    def __init__(self, command: str):
        self._commandString = command
        self._readCommand()

    def _readCommand(self) -> None:
        # reset argument list
        self._argList = []

        isEscaped = False
        isQuoted = False
        doubleQuotes = False
        currentArg = ''
        # process argument
        for char in self._commandString:
            # this character wasn't escaped, so handle special cases
            if not isEscaped:
                # handle double quotes
                if char == '"':
                    # a quoting is active
                    if isQuoted:
                        # end quoting
                        if doubleQuotes:
                            isQuoted = False
                            continue
                    # start a new quoting
                    else:
                        isQuoted = True
                        doubleQuotes = True
                        continue
                # single quoted argument
                elif char == "'":
                    # a quoting is active
                    if isQuoted:
                        # end quoting
                        if not doubleQuotes:
                            isQuoted = False
                            continue
                    # start a new quoting
                    else:
                        isQuoted = True
                        doubleQuotes = False
                        continue
                # space character
                elif char == ' ' or char == '\t':
                    # this space only marks a new argument if not quoted
                    if not isQuoted:
                        # add command if it exists
                        if currentArg != '':
                            self._argList.append(currentArg)
                        currentArg = ''
                        continue
                # escape character
                elif char == '\\':
                    isEscaped = True
                    continue
            # the next character isn't escaped anymore
            else:
                isEscaped = False
            # this is a normal argument character
            currentArg += char
        # put last argument in, if one exists
        if currentArg != '':
            self._argList.append(currentArg)
            currentArg = ''

    def __repr__(self) -> str:
        return self._argList.__str__()

    def __len__(self) -> int:
        return len(self._argList)

    def __iter__(self) -> list:
        return self._argList

    def __getitem__(self, item: int) -> str:
        return self._argList[item]

    def getParameterValues(self, parameterList: list, allowMulti: bool = False) -> list or str:
        """
        Fetch the value(s) for the given parameter
        @type parameterList: list
        @param parameterList: List of names of parameters to fetch
        @type allowMulti: bool
        @param allowMulti: Fetch all matches
        @rtype: list or str
        @return: Fetched value(s)
        """
        indexList = []
        for i, j in enumerate(self._argList):
            if j in parameterList:
                indexList.append(i)

        # get corresponding values
        valueList = []
        for index in indexList:
            if len(self._argList) > index + 1:
                valueList.append(self._argList[index + 1])
                if not allowMulti:
                    break
        # single value
        if not allowMulti:
            if len(valueList) == 0:
                return ''
            else:
                return valueList[0]
        # multiple values allowed
        return valueList

    def __eq__(self, other: Any) -> bool:
        # compare to string
        if isinstance(other, str):
            return self._commandString == other
        # compare to other command
        elif isinstance(other, Command):
            return self._argList == other._argList
        # last resort
        else:
            return self._commandString == other
