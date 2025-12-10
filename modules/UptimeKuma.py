#!/usr/bin/python3

from .Module import Module


class UptimeKuma(Module):
    def __init__(self, subDomain):
        """A Uptime Kuma instance

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['uptime-kuma']
        super().__init__(subDomain)

    def _createEnvFile(self):
        """Put all required parameters into an .env file in the subdomains root directory"""
        self.exposedPort = self.getFreePort()
        with open(self.envFile, 'w') as envFile:
            envFile.write('DOMAIN=' + str(self.subDomain) + '\n')
            envFile.write('DOMAIN_ESCAPED=' + str(self.subDomain).replace('.', '-') + '\n')
            envFile.write('HTTP_PORT=' + str(self.exposedPort) + '\n')
            envFile.write('DOMAIN_PATH=' + self.subDomain.rootDir + '\n')
