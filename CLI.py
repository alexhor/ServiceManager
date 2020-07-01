#!/usr/bin/python3

import re, os
from os.path import isdir
from enum import Enum

from ServiceManager import ServiceManager
from Command import Command
from modules.ModuleLoader import ModuleLoader


class CommandReturnCode(Enum):
    Unknown = 0
    Success = 1
    Warning = 2
    Error = 3
    Exit = 4


class ConsoleMod:
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
    _currentSubDomain = None
    _currentDomain = None
    _currentSubDomain = None
    _serviceManager = ServiceManager()

    def __init__(self):
        """Start the interactive cluster editor"""
        # Start the interactive shell
        while True:
            commandReturn = self._getCommand()
            # Check if the shell should be terminated
            if commandReturn == CommandReturnCode.Exit:
                break

    def _getCommand(self):
        """Prompt the user to input another command and run it
        
        Returns:
            CommandReturnCode: The run commands return code
        """
        commandString = input(ConsoleMod.HEADER + 'ServiceManager>' + ConsoleMod.ENDC)
        command = Command(commandString)

        # No command was specified
        if len(command) == 0:
            return CommandReturnCode.Unknown

        # Exit the shell
        if command == 'exit':
            return CommandReturnCode.Exit

        # Domain commands
        commandReturnCode = self.__processDomainCommands(command)
        if commandReturnCode != CommandReturnCode.Unknown:
            return commandReturnCode

        # SubDomain commands
        commandReturnCode = self.__processSubDomainCommands(command)
        if commandReturnCode != CommandReturnCode.Unknown:
            return commandReturnCode

        # Module commands
        commandReturnCode = self.__processModuleCommands(command)
        if commandReturnCode != CommandReturnCode.Unknown:
            return commandReturnCode

        # The command couldn't be processed
        print(ConsoleMod.WARNING + 'command "' + commandString + '" couldn\'t be processed' + ConsoleMod.ENDC)
        return CommandReturnCode.Unknown

    def __processDomainCommands(self, command):
        """Process Domain related commands
        usage: [select|create|exit|delete|get|list|ls|current] [dm|domain] [DOMAIN]
        
        Args:
            command (string): The command input by the user
        
        Returns: The processed commands return code
        """
        # Make sure this is a domain command
        if len(command) not in range(2, 4) or (command[1] != 'dm' and command[1] != 'domain'):
            return CommandReturnCode.Unknown
        # Set variables
        commandName = command[0]
        domainName = command[2] if len(command) == 3 else ''

        # Select (and create if it doesn't exist) a domain
        if commandName == 'select' and domainName != '':
            # Tell user about possibly leaving a previous domain
            if self._currentDomain is not None:
                print('left domain "' + str(self._currentDomain))
            # Get the domain from the manager
            self._currentDomain = self._serviceManager.domain(domainName)
            print('selected domain "' + str(self._currentDomain) + '"')
            return CommandReturnCode.Success
        # Exit the current domain
        elif commandName == 'exit':
            print('left domain "' + str(self._currentDomain))
            self._currentDomain = None
            return CommandReturnCode.Success
        # Create a new domain
        elif commandName == 'create' and domainName != '':
            domain = self._serviceManager.domain(domainName)
            print('created domain "' + str(domain) + '"')
            return CommandReturnCode.Success
        # Delete a domain
        elif commandName == 'delete' and domainName != '':
            # Get the domain
            domain = self._serviceManager.domain(domainName)
            domainName = str(domain)
            # Now delete it
            self._serviceManager.deleteDomain(domain)
            print('deleted domain "' + domainName + '"')
            return CommandReturnCode.Success
        # Show the name of the currently selected domain
        elif commandName == 'current':
            print('current domain "' + str(self._currentDomain) + '"')
            return CommandReturnCode.Success
        # TODO: add a command to show a domains details
        # List all existing domains
        elif commandName == 'get' or commandName == 'list' or commandName == 'ls':
            print('available domains:')
            for domain in self._serviceManager.domains:
                print('\t', domain)
            return CommandReturnCode.Success
        # No matching command
        return CommandReturnCode.Unknown

    def __processSubDomainCommands(self, command):
        """Process SubDomain related commands
        usage: [select|create|exit|delete|get|list|ls|current] [sd|subdomain] [SUBDOMAIN]
        
        Args:
            command (string): The command input by the user
        
        Returns: The processed commands return code
        """
        # Make sure this is a subdomain command
        if len(command) not in range(2, 4) or (command[1] != 'sd' and command[1] != 'subdomain'):
            return CommandReturnCode.Unknown
        # A domain has to be selected for this
        if self._currentDomain is None:
            print(ConsoleMod.FAIL + 'a domain has to be selected' + ConsoleMod.ENDC)
            return CommandReturnCode.Error
        # Set variables
        commandName = command[0]
        subDomainName = command[2] if len(command) == 3 else ''

        # Select (and create if it doesn't exist) a subdomain
        if commandName == 'select' and subDomainName != '':
            # Tell user about possibly leaving a previous subdomain
            if self._currentSubDomain is not None:
                print('left subdomain "' + str(self._currentSubDomain))
            # Get the subdomain from the current domain
            self._currentSubDomain = self._currentDomain.subDomain(subDomainName)
            print('selected subdomain "' + str(self._currentSubDomain) + '"')
            return CommandReturnCode.Success
        # Exit the current domain
        elif commandName == 'exit':
            print('left subdomain "' + str(self._currentSubDomain))
            self._currentSubDomain = None
            return CommandReturnCode.Success
        # Create a new subdomain
        elif commandName == 'create' and subDomainName != '':
            subdomain = self._currentDomain.subDomain(subDomainName)
            print('created subdomain "' + str(subdomain) + '"')
            return CommandReturnCode.Success
        # Delete a subdomain
        elif commandName == 'delete' and subDomainName != '':
            # Get the subdomain
            subdomain = self._currentDomain.subDomain(subDomainName)
            subDomainName = str(subdomain)
            # Now delete it
            subdomain.delete()
            print('deleted subdomain "' + subDomainName + '"')
            return CommandReturnCode.Success
        # Show the name of the currently selected subdomain
        elif commandName == 'current':
            print('current subdomain "' + str(self._currentSubDomain) + '"')
            return CommandReturnCode.Success
        # TODO: add a command to show a subdomains details
        # List all existing subdomains for this domain
        elif commandName == 'get' or commandName == 'list' or commandName == 'ls':
            print('available subdomains:')
            for subdomain in self._currentDomain.subDomains:
                print('\t', subdomain)
            return CommandReturnCode.Success
        # No matching command
        return CommandReturnCode.Unknown

    def __processModuleCommands(self, command):
        """Process Module related commands
        usage: [add|create|delete|rm|clean|up|down|get|list|ls|current] [md|module] [MODULE]
        
        Args:
            command (string): The command input by the user
        
        Returns: The processed commands return code
        """
        # Make sure this is a module command
        if len(command) not in range(2, 4) or (command[1] != 'md' and command[1] != 'module'):
            return CommandReturnCode.Unknown
        # A subdomain has to be selected for this
        if self._currentSubDomain is None:
            print(ConsoleMod.FAIL + 'a subdomain has to be selected' + ConsoleMod.ENDC)
            return CommandReturnCode.Error
        # Set variables
        commandName = command[0]
        moduleName = command[2] if len(command) == 3 else ''

        # Add a new module to the current subdomain
        if (commandName == 'add' or commandName == 'create') and moduleName != '':
            # Create the module and add it to the subdomain
            module = ModuleLoader.new(moduleName, self._currentSubDomain)
            self._currentSubDomain.addModule(module)
            print('created module "' + str(module) + '"')
            return CommandReturnCode.Success
        # Delete a module from the current subdomain
        elif commandName == 'delete' or commandName == 'rm' or commandName == 'clean':
            moduleName = str(self._currentSubDomain.activeModule)
            self._currentSubDomain.deleteModule()
            print('deleted module "' + moduleName + '" from subdomain "' + str(self._currentSubDomain) + '"')
            return CommandReturnCode.Success
        # Bring all containers of this module up
        elif commandName == 'up':
            # A module has to be active for this
            if self._currentSubDomain.activeModule is None:
                print(ConsoleMod.FAIL + 'the current subdomain "' + str(self._currentSubDomain) + '" has no active module' + ConsoleMod.ENDC)
                return CommandReturnCode.Error
            # Bring up the module
            self._currentSubDomain.activeModule.up()
            print('module "' + str(self._currentSubDomain.activeModule) + '" is coming up')
            return CommandReturnCode.Success
        # Shut all containers of this module down
        elif commandName == 'down':
            # A module has to be active for this
            if self._currentSubDomain.activeModule is None:
                print(ConsoleMod.FAIL + 'the current subdomain "' + str(self._currentSubDomain) + '" has no active module' + ConsoleMod.ENDC)
                return CommandReturnCode.Error
            # Shut the containers down
            self._currentSubDomain.activeModule.down()
            print('module "' + str(self._currentSubDomain.activeModule) + '" is going down')
            return CommandReturnCode.Success
        # TODO: add a command to show container logs
        # TODO: add a command to show container status
        # TODO: add a command to show module status (up/down/warning/error)
        # TODO: add a command to show a modules details
        # Show the name of the module for the currently selected subdomain
        elif commandName == 'get' or commandName == 'list' or commandName == 'ls' or commandName == 'current':
            print('current module "' + str(self._currentSubDomain.activeModule) + '"')
            return CommandReturnCode.Success
        # No matching command
        return CommandReturnCode.Unknown


if __name__ == '__main__':
    # Open the command line interface
    CLI()
