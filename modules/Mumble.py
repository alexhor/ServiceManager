#!/usr/bin/python3

from .Module import Module


class Mumble(Module):
    def __init__(self, subDomain):
        """A Mumble installation

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['mumble']
        super().__init__(subDomain)

    def _getCustomEnvVars(self) -> dict[str, str]:
        self.exposedPort = self.getFreePort()
        return {
            'HTTP_PORT': str(self.exposedPort),
        }
