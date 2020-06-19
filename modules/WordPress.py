#!/usr/bin/python3

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
            envFile.write('DOMAIN=' + self.subDomain.__str__() + '\n')
            envFile.write('HTTP_PORT=' + self.exposedPort.__str__() + '\n')
            envFile.write('DOMAIN_PATH=' + self.subDomain.rootDir + '\n')
            envFile.write('MYSQL_PASSWORD=' + self.password() + '\n')
            envFile.write('MYSQL_ROOT_PASSWORD=' + self.password() + '\n')
