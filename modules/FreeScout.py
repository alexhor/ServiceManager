#!/usr/bin/python3

from .Webserver import Webserver
from .MySql import MySql
from .Module import Module


class FreeScout(Webserver, MySql, Module):
    def __init__(self, subDomain):
        """A FreeScout installation

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['mysql', 'data']
        super().__init__(subDomain)

    def _createEnvFile(self):
        """Put all required parameters into an .env file in the subdomains root directory"""
        with open(self.envFile, 'w') as envFile:
            envFile.write('DOMAIN=' + str(self.subDomain) + '\n')
            envFile.write('DOMAIN_ESCAPED=' + str(self.subDomain).replace('.', '-') + '\n')
            envFile.write('DOMAIN_URL=https://' + str(self.subDomain))
            envFile.write('DOMAIN_PATH=' + self.subDomain.rootDir + '\n')
            envFile.write('MYSQL_PASSWORD=' + self.password() + '\n')
            envFile.write('MYSQL_ROOT_PASSWORD=' + self.password() + '\n')

