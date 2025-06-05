#!/usr/bin/python3

from enum import Enum
from prompt_toolkit import PromptSession

from CliCompleter import CliCompleter
from ServiceManager import ServiceManager
from modules.ModuleLoader import ModuleLoader

class CommandReturnCode(Enum):
    Unknown = 0
    Success = 1
    Warning = 2
    Error = 3
    Exit = 4


class ConsoleMod(Enum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class CLI:
    """A command line service manager"""

    def __init__(self):
        """Start the interactive service manager"""
        self._service_manager = ServiceManager()

        self._session = PromptSession(completer=CliCompleter(self._service_manager))
        self.run()

    def run(self):
        """Run prompt session"""
        while True:
            try:
                user_input = self._session.prompt("ServiceManager> ")
                if user_input.strip() in ["exit", "quit"]:
                    break
                self.process_command(user_input.strip())
            except KeyboardInterrupt:
                continue
            except EOFError:
                break

    def process_command(self, command: str):
        commandParts = command.strip().split(' ')

        # Domain commands
        if 'domain' == commandParts[0] or 'dm' == commandParts[0]:
            if 2 > len(commandParts):
                pass
            elif 'exit' == commandParts[1]:
                self._service_manager.currentDomain = None
                self._service_manager.currentSubDomain = None
                print("Domain unselected")
                return
            elif 'get' == commandParts[1] or 'current' == commandParts[1]:
                if None is self._service_manager.currentDomain:
                    print("No domain selected")
                else:
                    print(self._service_manager.currentDomain.name)
                return
            elif 'list' == commandParts[1] or 'ls' == commandParts[1]:
                if 0 == len(self._service_manager.domains):
                    print("No domains exist")
                else:
                    print("Existing domains:")
                    for domain in self._service_manager.domains:
                        print(" ", domain)
                return
            elif 'select' == commandParts[1] or 'create' == commandParts[1]:
                if 3 == len(commandParts):
                    self._service_manager.currentDomain = self._service_manager.domain(commandParts[2])
                    self._service_manager.currentSubDomain = None
                    print("Domain", commandParts[2], "selected")
                    return
            elif 'delete' == commandParts[1]:
                if 3 == len(commandParts):
                    self._service_manager.deleteDomain(commandParts[2])
                    self._service_manager.currentDomain = None
                    self._service_manager.currentSubDomain = None
                    print("Domain", commandParts[2], "delted")
                    return
            else:
                print("Usage:\tdomain COMMAND [DOMAIN]")
                print("\tdm COMMAND [DOMAIN]")
                print()
                print("Available Commands:")
                print(" ", "get (current)\tGet the currently selected domain")
                print(" ", "list (ls)\tList all existing top level domains")
                print(" ", "select\tSelect a top level domain\n\t\tCreates the domain if it doesn't exist yet")
                print(" ", "create\tCreate a new top level domain\n\t\tOnly selects the domain if it already exists")
                print(" ", "delete\tDelete an existing top level domain")
                print(" ", "exit\t\tUnselect the currently selected top level domain")
                print(" ", "help\t\tDisplay this help")
                return
        # Subdomain commands
        elif 'subdomain' == commandParts[0] or 'sd' == commandParts[0]:
            if None is self._service_manager.currentDomain:
                print("No domain selected")
                return
            elif 2 > len(commandParts):
                pass
            elif 'exit' == commandParts[1]:
                self._service_manager.currentSubDomain = None
                print("Subdomain unselected")
                return
            elif 'get' == commandParts[1] or 'current' == commandParts[1]:
                if None is self._service_manager.currentSubDomain:
                    print("No subdomain selected")
                else:
                    print(self._service_manager.currentSubDomain.name)
                return
            elif 'list' == commandParts[1] or 'ls' == commandParts[1]:
                if 0 == len(self._service_manager.currentDomain.loadSubDomains()):
                    print("No subdomains exist")
                else:
                    print("Existing subdomains:")
                    for subdomain in self._service_manager.currentDomain.subDomains:
                        print(" ", subdomain)
                return
            elif 'select' == commandParts[1] or 'create' == commandParts[1]:
                if 3 == len(commandParts):
                    self._service_manager.currentSubDomain = self._service_manager.currentDomain.subDomain(commandParts[2])
                    print("Subdomain", commandParts[2], "selected")
                    return
            elif 'delete' == commandParts[1]:
                if 3 == len(commandParts):
                    self._service_manager.currentDomain.deleteSubDomain(commandParts[2])
                    self._service_manager.currentSubDomain = None
                    print("Subdomain", commandParts[2], "delted")
                    return
            else:
                print("Usage:\tsubdomain COMMAND [SUBDOMAIN]")
                print("\tsd COMMAND [SUBDOMAIN]")
                print()
                print("Available Commands:")
                print(" ", "get (current)\tGet the currently selected subdomain")
                print(" ", "list (ls)\tList all existing subdomains under the currently selected top level domain")
                print(" ", "select\tSelect a subdomain under the currently selected top level domain\n\t\tCreates the subdomain if it doesn't exist yet")
                print(" ", "create\tCreate a new subdomain under the currently selected top level domain\n\t\tOnly selects the subdomain if it already exists")
                print(" ", "delete\tDelete an existing subdomain under the currently selected top level domain")
                print(" ", "exit\t\tUnselect the currently selected subdomain")
                print(" ", "help\t\tDisplay this help")
                return
        # Module commands
        elif 'module' == commandParts[0] or 'md' == commandParts[0]:
            if None is self._service_manager.currentDomain:
                print("No domain selected")
                return
            if None is self._service_manager.currentSubDomain:
                print("No subdomain selected")
                return
            elif 2 > len(commandParts):
                pass
            elif 'list' == commandParts[1] or 'ls' == commandParts[1]:
                print("Available modules:")
                for module in ModuleLoader.availableModules:
                    print(" ", module)
                return
            elif 'add' == commandParts[1] or 'create' == commandParts[1]:
                if 3 == len(commandParts):
                    module = ModuleLoader.new(commandParts[2], self._service_manager.currentSubDomain)
                    self._service_manager.currentSubDomain.addModule(module)
                    print("Module", commandParts[2], "added")
                    return
            # TODO: add a command to show container logs
            # TODO: add a command to show container status
            # TODO: add a command to show module status (up/down/warning/error)
            # TODO: add a command to show a modules details
            elif commandParts[1] in ('up', 'down', 'get', 'current', 'log', 'delete', 'rm', 'clean') and self._service_manager.currentSubDomain.activeModule.isNone():
                print("No module configured for this subdomain")
                return
            elif 'up' == commandParts[1]:
                self._service_manager.currentSubDomain.activeModule.up()
                print("Module", self._service_manager.currentSubDomain.activeModule, "is coming up")
                return
            elif 'down' == commandParts[1]:
                self._service_manager.currentSubDomain.activeModule.down()
                print("Module", self._service_manager.currentSubDomain.activeModule, "is going down")
                return
            elif 'get' == commandParts[1] or 'current' == commandParts[1]:
                print(self._service_manager.currentSubDomain.activeModule)
                return
            elif 'log' == commandParts[1]:
                if 3 == len(commandParts):
                    self._service_manager.currentSubDomain.activeModule.showContainerLogs(commandParts[2])
                    return
            elif 'command' == commandParts[1] or 'cmd' == commandParts[1]:
                if 3 <= len(commandParts):
                    command = ' '.join(commandParts[3:]) if 4 <= len(commandParts) else '/bin/bash'
                    self._service_manager.currentSubDomain.activeModule.runContainerCmd(commandParts[2], command)
                    return
            elif 'delete' == commandParts[1] or 'rm' == commandParts[1] or 'clean' == commandParts[1]:
                moduleName = str(self._service_manager.currentSubDomain.activeModule)
                self._service_manager.currentSubDomain.deleteModule()
                print("Module", moduleName, "delted")
                return
            else:
                print("Usage:\tmodule COMMAND [MODULE]")
                print("\tmd COMMAND [MODULE]")
                print()
                print("Available Commands:")
                print(" ", "up\t\t\tBring all the modules docker containers up")
                print(" ", "down\t\t\tTear all the modules docker containers down")
                print(" ", "get\t (current)\tGet the configured module for the selected subdomain")
                print(" ", "list\t (ls)\t\tList all available modules")
                print(" ", "add\t (create)\tSet the module for the selected subdomain")
                print(" ", "log\t\t\tShow a containers log output")
                print(" ", "command\t (cmd)\tRun an interactive command in a container (default: /bin/bash)")
                print(" ", "delete (rm|clean)\tDelete any module form the selected subdomain")
                print(" ", "help\t\t\tDisplay this help")
                return
        # Display help
        print("Available Commands:")
        print(" ", "domain\t(dm)\tManage top level domains")
        print(" ", "subdomain\t(sd)\tManage subdomains of the currently selected top level domain")
        print(" ", "module\t(md)\tManage the module of the currently selected subdomain")


if __name__ == '__main__':
    # Open the command line interface
    CLI()
