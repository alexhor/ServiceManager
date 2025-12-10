#!/usr/bin/python3

from os import makedirs
from os.path import isdir

from distutils.dir_util import copy_tree

from .Module import Module
from .MySql import MySql


class Webserver(MySql, Module):
    def __init__(self, subDomain):
        """A php Webserver with Mysql

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['php']
        super().__init__(subDomain)

    def _createEnvFile(self):
        """Put all required parameters into an .env file in the subdomains root directory"""
        self.exposedPort = self.getFreePort()
        with open(self.envFile, 'w') as envFile:
            envFile.write('DOMAIN=' + str(self.subDomain) + '\n')
            envFile.write('DOMAIN_ESCAPED=' + str(self.subDomain).replace('.', '-') + '\n')

    def copyData(self, dataDir, webDir='httpdocs'):
        """Import a web directory

        Args:
            dataDir (string): Location of the data to import
            webDir (string): The webservers data directory in the subdomain folder
        """
        if not isdir(dataDir) or 'DOMAIN_PATH' not in self.envFileDict.keys():
            return
        if not isdir(self.envFileDict['DOMAIN_PATH']):
            makedirs(self.envFileDict['DOMAIN_PATH'])
        print(copy_tree(dataDir, self.envFileDict['DOMAIN_PATH'] + '/' + webDir, preserve_mode=1, preserve_times=1, preserve_symlinks=1, update=0, verbose=1, dry_run=0))
