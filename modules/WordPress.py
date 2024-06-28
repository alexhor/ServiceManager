#!/usr/bin/python3

from os import makedirs
from os.path import isfile, isdir
from subprocess import run
from distutils.dir_util import copy_tree

from .Webserver import Webserver
from .MySql import MySql
from .Module import Module


class WordPress(Webserver, MySql, Module):
    def __init__(self, subDomain):
        """A WordPress installation
        
        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['mysql', 'wordpress']
        super().__init__(subDomain)

    def _createEnvFile(self):
        """Put all requried parameters into an .env file in the subdomains root directory"""
        self.exposedPort = self.getFreePort()
        with open(self.envFile, 'w') as envFile:
            envFile.write('DOMAIN=' + str(self.subDomain) + '\n')
            envFile.write('DOMAIN_ESCAPED=' + str(self.subDomain).replace('.', '-') + '\n')
            envFile.write('HTTP_PORT=' + str(self.exposedPort) + '\n')
            envFile.write('DOMAIN_PATH=' + self.subDomain.rootDir + '\n')
            envFile.write('MYSQL_PASSWORD=' + self.password() + '\n')
            envFile.write('MYSQL_ROOT_PASSWORD=' + self.password() + '\n')

