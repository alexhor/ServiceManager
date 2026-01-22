#!/usr/bin/python3

from os.path import join

from .Codeigniter import Codeigniter
from .Collabora import Collabora
from .FreeScout import FreeScout
from .Leantime import Leantime
from .LinkStack import LinkStack
from .Module import Module
from .Mumble import Mumble
from .Nextcloud import Nextcloud
from .NoneModule import NoneModule
from .OAuthWebserver import OAuthWebserver
from .Odoo import Odoo
from .ParseDmarc import ParseDmarc
from .Registry import Registry
from .UptimeKuma import UptimeKuma
from .Webserver import Webserver
from .WordPress import WordPress
from .Yopass import Yopass
from .Zammad import Zammad


class ModuleLoader:
    availableModules = {
        'Codeigniter'   : Codeigniter,
        'Collabora'     : Collabora,
        'FreeScout'     : FreeScout,
        'Leantime'      : Leantime,
        'LinkStack'     : LinkStack,
        'Mumble'        : Mumble,
        'Nextcloud'     : Nextcloud,
        'OAuthWebserver': OAuthWebserver,
        'Odoo'          : Odoo,
        'ParseDmarc'    : ParseDmarc,
        'Registry'      : Registry,
        'UptimeKuma'    : UptimeKuma,
        'Webserver'     : Webserver,
        'WordPress'     : WordPress,
        'Yopass'        : Yopass,
        'Zammad'        : Zammad,
    }

    @staticmethod
    def load(subDomain) -> Module:
        """Load a module for the given subdomain, if one exists

        Args:
            subDomain (SubDomain): The subDomain to load the module for
        """
        moduleSettings = Module.fileToDict(join(subDomain.rootDir, '.module'))
        # If the module doesn't exist, return a dummy one
        if 'MODULE_NAME' not in moduleSettings.keys() or \
                moduleSettings['MODULE_NAME'] not in ModuleLoader.availableModules.keys():
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
