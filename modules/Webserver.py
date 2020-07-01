#!/usr/bin/python3

from os import makedirs
from os.path import isfile, isdir
from subprocess import run
from distutils.dir_util import copy_tree


class Webserver:
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
