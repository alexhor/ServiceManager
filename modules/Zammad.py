#!/usr/bin/python3

from .Webserver import Webserver
from .Module import Module


class Zammad(Webserver, Module):
    def __init__(self, subDomain):
        """A Zammad installation
        
        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['zammad', 'zammad-backup', 'elasticsearch', 'postgresql']
        super().__init__(subDomain)

    def _createEnvFile(self):
        """Put all requried parameters into an .env file in the subdomains root directory"""
        self.exposedPort = self.getFreePort()
        with open(self.envFile, 'w') as envFile:
            envFile.write('DOMAIN=' + str(self.subDomain) + '\n')
            envFile.write('DOMAIN_ESCAPED=' + str(self.subDomain).replace('.', '-') + '\n')
            envFile.write('HTTP_PORT=' + str(self.exposedPort) + '\n')
            envFile.write('DOMAIN_PATH=' + self.subDomain.rootDir + '\n')
            envFile.write('POSTGRES_USER=zammad\n')
            envFile.write('POSTGRES_PASSWORD=' + self.password(30) + '\n')
            envFile.write('IMAGE_REPO=zammad/zammad-docker-compose\n')
            envFile.write('VERSION=-latest\n')

