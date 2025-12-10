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

    def _getCustomEnvVars(self) -> dict[str, str]:
        self.exposedPort = self.getFreePort()
        return {
            'HTTP_PORT': str(self.exposedPort),
        }
