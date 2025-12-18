#!/usr/bin/python3

from os.path import isfile, join

from .Codeigniter import Codeigniter
from .Collabora import Collabora
from .FreeScout import FreeScout
from .Module import Module
from .Mumble import Mumble
from .Nextcloud import Nextcloud
from .NoneModule import NoneModule
from .Odoo import Odoo
from .UptimeKuma import UptimeKuma
from .Webserver import Webserver
from .WordPress import WordPress
from .Zammad import Zammad


class ModuleLoader:
    availableModules = {
        'Codeigniter': Codeigniter,
        'Collabora'  : Collabora,
        'FreeScout'  : FreeScout,
        'Mumble'     : Mumble,
        'Nextcloud'  : Nextcloud,
        'Odoo'       : Odoo,
        'UptimeKuma' : UptimeKuma,
        'Webserver'  : Webserver,
        'WordPress'  : WordPress,
        'Zammad'     : Zammad,
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
    def load(subDomain) -> Module:
        """Load a module for the given subdomain, if one exists

        Args:
            subDomain (SubDomain): The subDomain to load the module for
        """
        moduleSettings = ModuleLoader.fileToDict(join(subDomain.rootDir, '.module'))
        # If the module doesn't exist, return a dummy one
        if 'MODULE_NAME' not in moduleSettings.keys() or moduleSettings['MODULE_NAME'] not in ModuleLoader.availableModules.keys():
            return NoneModule(subDomain)
        # Otherwise load the module
        else:
            return ModuleLoader.availableModules[moduleSettings['MODULE_NAME']](subDomain)

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
        if moduleName not in ModuleLoader.availableModules.keys():
            return NoneModule(subDomain)
        # Otherwise create the module
        else:
            return ModuleLoader.availableModules[moduleName](subDomain)
