#!/usr/bin/python3

from abc import ABC, abstractmethod
from typing import Generator

from prompt_toolkit.completion import Completion

from ServiceManager import ServiceManager
from modules.ModuleLoader import ModuleLoader


class Command:
    def __init__(self, command: str, aliasList: list[str] = [], subcommandList: list['Command'] = [], argList: list['Argument'] = []):
        self._command: str = command
        self.__aliasList: list[str] = aliasList
        self._subcommandList: list[Command] = subcommandList
        self._argList: list[Argument] = argList

    # Command
    @property
    def command(self) -> str:
        return self._command

    # Alias
    @property
    def aliasList(self) -> tuple[str]:
        return tuple(self.__aliasList)

    def addAlias(self, alias: str):
        if alias in self.__aliasList:
            return
        self.__aliasList.append(alias)

    # Subcommand
    @property
    def subcommandList(self) -> tuple['Command']:
        return tuple(self._subcommandList)

    def addSubcommand(self, subcommand: 'Command'):
        if subcommand in self._subcommandList:
            return
        self._subcommandList.append(subcommand)

    # Argument
    @property
    def argumentList(self) -> tuple['Argument']:
        return tuple(self._argList)

    def addArgument(self, argument: 'Argument'):
        if argument in self._argList:
            return
        self._argList.append(argument)


class Argument(ABC):
    def __init__(self, serviceManager):
        self._serviceManager: ServiceManager = serviceManager

    @abstractmethod
    def yieldCompletion(self, firstLevelText: str) -> Generator[Completion, None, None]:
        pass


class ArgumentDomain(Argument):
    def yieldCompletion(self, text: str) -> Generator[Completion, None, None]:
        for domain in self._serviceManager.domains.values():
            if domain.name.startswith(text):
                yield Completion(domain.name, start_position=-1 * len(text))


class ArgumentSubDomain(Argument):
    def yieldCompletion(self, text: str) -> Generator[Completion, None, None]:
        if None is self._serviceManager.currentDomain:
            yield Completion(" ", start_position=-1, display="No top level domain selected")
        else:
            for subdomain in self._serviceManager.currentDomain.loadSubDomains().values():
                if subdomain.subName.startswith(text):
                    yield Completion(subdomain.subName, start_position=-1 * len(text), display=subdomain.name)


class ArgumentModule(Argument):
    def yieldCompletion(self, text: str) -> Generator[Completion, None, None]:
        if None is self._serviceManager.currentSubDomain:
            yield Completion(" ", start_position=-1, display="No subdomain selected")
        else:
            for module in ModuleLoader.availableModules:
                if module.startswith(text):
                    yield Completion(module, start_position=-1 * len(text))


class ArgumentContainer(Argument):
    def yieldCompletion(self, text: str) -> Generator[Completion, None, None]:
        if None is self._serviceManager.currentSubDomain:
            yield Completion(" ", start_position=-1, display="No subdomain selected")
        else:
            for containerName in self._serviceManager.currentSubDomain.activeModule.getContainers():
                if containerName.startswith(text):
                    yield Completion(containerName, start_position=-1 * len(text))
