#!/usr/bin/python3

from .Module import Module


class LinkStack(Module):
    """
    A LinkStack instance.

    LinkStack is an alternative to LinkTree.
    """

    def __init__(self, subDomain):
        self.requiredDirs = ['src']
        super().__init__(subDomain)

    def _getCustomEnvVars(self) -> dict[str, str]:
        self.exposedPort = self.getFreePort()
        return {
            'ADMIN_EMAIL': str(self.exposedPort),
            'TIMEZONE'   : 'Europe/Berlin'
        }
