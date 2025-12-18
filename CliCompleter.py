from typing import Generator

from prompt_toolkit.completion import Completer, Completion

from Command import ArgumentContainer, ArgumentModule, Command, ArgumentDomain, ArgumentSubDomain


class CliCompleter(Completer):
    def __init__(self, service_manager):
        self._service_manager = service_manager

        self._commands: tuple[Command, ...] = (
            Command("domain", ["dm"], [
                Command("get", ["current"]),
                Command("list", ["ls"]),
                Command("select", argList=[ArgumentDomain(self._service_manager)]),
                Command("create", argList=[ArgumentDomain(self._service_manager)]),
                Command("delete", argList=[ArgumentDomain(self._service_manager)]),
                Command("exit"),
                Command("help"),
            ]),
            Command("subdomain", ["sd"], [
                Command("get", ["current"]),
                Command("list", ["ls"]),
                Command("select", argList=[ArgumentSubDomain(self._service_manager)]),
                Command("create", argList=[ArgumentSubDomain(self._service_manager)]),
                Command("delete", argList=[ArgumentSubDomain(self._service_manager)]),
                Command("exit"),
                Command("help"),
            ]),
            Command("module", ["md"], [
                Command("up"),
                Command("down"),
                Command("get", ["current"]),
                Command("list", ["ls"]),
                Command("add", ["create"], argList=[ArgumentModule(self._service_manager)]),
                Command("log", argList=[ArgumentContainer(self._service_manager)]),
                Command("command", ["cmd"], argList=[ArgumentContainer(self._service_manager)]),
                Command("delete", ["rm", "clean"]),
                Command("help"),
            ]),
            Command("help"),
            Command("exit", ["quit"]),
        )

    def get_completions_recursive(self, text: str, command: Command = None) -> Generator[str, None, None]:
        textSplit = text.split(' ')
        firstLevelText = textSplit.pop(0)
        firstLevelCommand = None
        commandList = command.subcommandList if None is not command else self._commands
        for cmd in commandList:
            if 0 < len(textSplit):
                if cmd.command == firstLevelText or firstLevelText in cmd.aliasList:
                    firstLevelCommand = cmd
            else:
                if cmd.command.startswith(firstLevelText):
                    yield Completion(cmd.command, start_position=-1 * len(firstLevelText))
                for alias in cmd.aliasList:
                    if alias.startswith(firstLevelText):
                        yield Completion(alias, start_position=-1 * len(firstLevelText))

        if 0 < len(textSplit):
            if None is not firstLevelCommand:
                yield from self.get_completions_recursive(' '.join(textSplit), firstLevelCommand)
        elif None is not command:
            for argument in command.argumentList:
                yield from argument.yieldCompletion(firstLevelText)

    def get_completions(self, document, complete_event) -> Generator[str, None, None]:
        text = document.text_before_cursor
        yield from self.get_completions_recursive(text)
