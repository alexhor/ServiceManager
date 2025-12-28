#!/usr/bin/python3

from .Module import Module


class FreeScout(Module):
    def __init__(self, subDomain):
        """A FreeScout installation

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['mariadb', 'data']
        super().__init__(subDomain)

    def _getCustomEnvVars(self) -> dict[str, str]:
        return {
            'MARIADB_PASSWORD'     : self.password(),
            'MARIADB_ROOT_PASSWORD': self.password(),
        }
