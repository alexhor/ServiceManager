#!/usr/bin/python3

from os import chown
from os.path import join

from .Module import Module


class Zammad(Module):
    def __init__(self, subDomain):
        """A Zammad installation

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['zammad', 'zammad-backup', 'elasticsearch', 'postgresql', 'redis']
        super().__init__(subDomain)
        # Fix elasticsearch permissions
        chown(join(self.subDomain.rootDir, 'elasticsearch'), 1001, 1001)

    def _createEnvFile(self):
        """Put all required parameters into an .env file in the subdomains root directory"""
        self.exposedPort = self.getFreePort()
        with open(self.envFile, 'w') as envFile:
            envFile.write('DOMAIN=' + str(self.subDomain) + '\n')
            envFile.write('DOMAIN_ESCAPED=' + str(self.subDomain).replace('.', '-') + '\n')
            envFile.write('HTTP_PORT=' + str(self.exposedPort) + '\n')
            envFile.write('DOMAIN_PATH=' + self.subDomain.rootDir + '\n')
            envFile.write('POSTGRES_USER=afaf\n')
            envFile.write('POSTGRES_PASSWORD=' + self.password(30) + '\n')
            envFile.write('IMAGE_REPO=zammad/zammad-docker-compose\n')
            envFile.write('VERSION=-latest\n')
