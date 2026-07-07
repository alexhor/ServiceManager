#!/usr/bin/python3

from .Module import Module


class Zammad(Module):
    def __init__(self, subDomain):
        """A Zammad installation

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['zammad-storage', 'zammad-backup', 'elasticsearch-data', 'postgresql-data', 'redis-data']
        super().__init__(subDomain)

    def _getCustomEnvVars(self) -> dict[str, str]:
        return {
            'POSTGRES_USER': 'zammad',
            'POSTGRES_PASS': self.password(30),
            'VERSION'      : '7',
        }
