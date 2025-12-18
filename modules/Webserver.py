#!/usr/bin/python3

from os import makedirs
from os.path import isdir, join
from pathlib import Path

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

    def up(self):
        # Create php.ini file - otherwise, docker compose will make the mount a directory
        Path(join(self.subDomain.rootDir, 'php.ini')).touch()
        # Call super
        super().up()

    def copyData(self, dataDir, webDir='httpdocs'):
        """Import a web directory

        Args:
            dataDir (string): Location of the data to import
            webDir (string): The webservers data directory in the subdomain folder
        """
        if not isdir(dataDir) or 'DOMAIN_PATH' not in self.envVars.keys():
            return
        if not isdir(self.envVars['DOMAIN_PATH']):
            makedirs(self.envVars['DOMAIN_PATH'])
        print(copy_tree(dataDir, self.envVars['DOMAIN_PATH'] + '/' + webDir, preserve_mode=1, preserve_times=1, preserve_symlinks=1, update=0, verbose=1, dry_run=0))
