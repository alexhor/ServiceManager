#!/usr/bin/python3

from os.path import isfile, join

from .NoneModule import NoneModule
from .Webserver import Webserver
from .WordPress import WordPress
from .Nextcloud import Nextcloud
from .Zammad import Zammad
from .Odoo import Odoo
from .UptimeKuma import UptimeKuma

class ModuleLoader:
    __availableModules = {
        'Webserver' :   Webserver,
        'WordPress' :   WordPress,
        'Nextcloud' :   Nextcloud,
        'Zammad'    :   Zammad,
        'Odoo'      :   Odoo,
        'UptimeKuma':   UptimeKuma,
    }

    @staticmethod
    def fileToDict(filePath):
        """Get a dictionary representation of a file
        
        Args:
            filePath (string): Path to the file to convert
        Returns:
            dict: The converted file
        """
        if not isfile(filePath):
            return dict()
        envVars = dict()
        with open(filePath, 'r') as file:
            for line in file:
                splitLine = line.strip().split('=', 1)
                # Skip invalid lines
                if len(splitLine) != 2:
                    continue
                envVars[splitLine[0]] = splitLine[1]
        return envVars

    @staticmethod
    def load(subDomain):
        """Load a module for the given subdomain, if one exists
        
        Args:
            subDomain (SubDomain): The subDomain to load the module for
        """
        moduleSettings = ModuleLoader.fileToDict(join(subDomain.rootDir, '.module'))
        # If the module doesn't exist, return a dummy one
        if 'MODULE_NAME' not in moduleSettings.keys() or moduleSettings['MODULE_NAME'] not in ModuleLoader.__availableModules.keys():
            return NoneModule(subDomain)
        # Otherwise load the module
        else:
            return ModuleLoader.__availableModules[moduleSettings['MODULE_NAME']](subDomain)

    @staticmethod
    def new(moduleName, subDomain):
        """Create a new module of the given type
        
        Args:
            moduleName (string): Name of the module type to create a new instance of
            subDomain (SubDomain): The subDomain to create the module for
        
        Returns:
            Module: The created module
        """
        # If the module doesn't exist, return a dummy one
        if moduleName not in ModuleLoader.__availableModules.keys():
            return NoneModule(subDomain)
        # Otherwise create the module
        else:
            return ModuleLoader.__availableModules[moduleName](subDomain)
