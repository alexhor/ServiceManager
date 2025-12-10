#!/usr/bin/python3

from .Module import Module
from .MySql import MySql
from .Webserver import Webserver


class FreeScout(Webserver, MySql, Module):
    def __init__(self, subDomain):
        """A FreeScout installation

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['mysql', 'data']
        super().__init__(subDomain)

    def _getCustomEnvVars(self) -> dict[str, str]:
        return {
            'MYSQL_PASSWORD'     : self.password(),
            'MYSQL_ROOT_PASSWORD': self.password(),
        }
