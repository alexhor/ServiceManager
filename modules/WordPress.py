#!/usr/bin/python3

from os import makedirs
from os.path import isfile, isdir
from subprocess import run
from distutils.dir_util import copy_tree

from .Module import Module


class WordPress(Module):
    def __init__(self, subDomain):
        """A WordPress installation
        
        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['mysql', 'wordpress']
        super().__init__(subDomain, 'wordpress')

    def _createEnvFile(self):
        """Put all requried parameters into an .env file in the subdomains root directory"""
        self.exposedPort = self.getFreePort()
        with open(self.envFile, 'w') as envFile:
            envFile.write('DOMAIN_ESCAPED=' + str(self.subDomain).replace('.', '-') + '\n')
            envFile.write('HTTP_PORT=' + str(self.exposedPort) + '\n')
            envFile.write('DOMAIN_PATH=' + self.subDomain.rootDir + '\n')
            envFile.write('MYSQL_PASSWORD=' + self.password() + '\n')
            envFile.write('MYSQL_ROOT_PASSWORD=' + self.password() + '\n')

    def importDb(self, dbLocation):
        """Import an sql dump
        
        Args:
            dbLocation (string): Location of an sql file
        """
        if not isfile(dbLocation) or 'DOMAIN_ESCAPED' not in self.envFileDict.keys() or 'MYSQL_ROOT_PASSWORD' not in self.envFileDict.keys():
            return
        print(dbLocation)
        run('cat ' + dbLocation + ' | docker exec -i ' + self.envFileDict['DOMAIN_ESCAPED'] + '_mysql mysql -uroot -p' + self.envFileDict['MYSQL_ROOT_PASSWORD'], shell=True)
        print('DONE')

    def copyData(self, dataDir):
        """Import (part of) a wordpress directory

        Args:
            dataDir (string): Location of the wordpress data to import
        """
        if not isdir(dataDir) or 'DOMAIN_PATH' not in self.envFileDict.keys():
            return
        if not isdir(self.envFileDict['DOMAIN_PATH']):
            makedirs(self.envFileDict['DOMAIN_PATH'])
        print(copy_tree(dataDir, self.envFileDict['DOMAIN_PATH'] + '/wordpress', preserve_mode=1, preserve_times=1, preserve_symlinks=1, update=0, verbose=1, dry_run=0))
