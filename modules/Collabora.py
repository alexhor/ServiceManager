#!/usr/bin/python3

from .Module import Module


class Collabora(Module):
    def __init__(self, subDomain):
        """A Collabora installation

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = []
        super().__init__(subDomain)

    def _createEnvFile(self):
        """Put all required parameters into an .env file in the subdomains root directory"""
        with open(self.envFile, 'w') as envFile:
            envFile.write('DOMAIN=' + str(self.subDomain) + '\n')
            envFile.write('DOMAIN_ESCAPED=' + str(self.subDomain).replace('.', '-') + '\n')
            envFile.write('DOMAIN_URL=https://' + str(self.subDomain))
            envFile.write('DOMAIN_PATH=' + self.subDomain.rootDir + '\n')
            envFile.write('ADMIN_PASSWORD=' + self.password() + '\n')
