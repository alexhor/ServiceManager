#!/usr/bin/python3

from os.path import isfile
from subprocess import run


class MySql:
    def importDb(self, dbLocation):
        """Import an sql dump
        
        Args:
            dbLocation (string): Location of an sql file
        """
        if not isfile(dbLocation) or 'DOMAIN_ESCAPED' not in self.envFileDict.keys() or 'MYSQL_ROOT_PASSWORD' not in self.envFileDict.keys():
            return
        run('cat ' + dbLocation + ' | docker exec -i ' + self.envFileDict['DOMAIN_ESCAPED'] + '_mysql mysql -uroot -p' + self.envFileDict['MYSQL_ROOT_PASSWORD'], shell=True)

    def mysqlAccess(self):
        """Get a mysql command prompt in the mysql container"""
        run('docker exec -it ' + self.envFileDict['DOMAIN_ESCAPED'] + '_mysql mysql -uroot -p' + self.envFileDict['MYSQL_ROOT_PASSWORD'], shell=True)

