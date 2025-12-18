#!/usr/bin/python3

from .Module import Module
from .MySql import MySql
from .Webserver import Webserver


class WordPress(Webserver, MySql, Module):
    def __init__(self, subDomain):
        """A WordPress installation

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['mysql', 'wordpress']
        super().__init__(subDomain)

    def _getCustomEnvVars(self) -> dict[str, str]:
        self.exposedPort = self.getFreePort()
        return {
            'HTTP_PORT'          : str(self.exposedPort),
            'MYSQL_PASSWORD'     : self.password(),
            'MYSQL_ROOT_PASSWORD': self.password(),
        }
