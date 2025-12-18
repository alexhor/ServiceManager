#!/usr/bin/python3
from os import chown
from os.path import join

from .Module import Module


class LinkStack(Module):
    """
    A LinkStack instance.

    LinkStack is an alternative to LinkTree.
    """

    def __init__(self, subDomain):
        self.requiredDirs = ['src']
        super().__init__(subDomain)
        # Fix folder permissions
        chown(join(self.subDomain.rootDir, 'src'), 100, 101)

    def _getCustomEnvVars(self) -> dict[str, str]:
        self.exposedPort = self.getFreePort()
        return {
            'ADMIN_EMAIL': 'invalid@example.com',
            'TIMEZONE'   : 'Europe/Berlin'
        }
