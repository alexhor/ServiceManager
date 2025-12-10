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

    def _getCustomEnvVars(self) -> dict[str, str]:
        return {
            'ADMIN_PASSWORD': self.password(),
        }
