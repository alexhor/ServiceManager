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

    def _getCustomEnvVars(self) -> dict[str, str]:
        self.exposedPort = self.getFreePort()
        return {
            'HTTP_PORT'        : str(self.exposedPort),
            'POSTGRES_USER'    : 'afaf',
            'POSTGRES_PASSWORD': self.password(30),
            'IMAGE_REPO'       : 'zammad/zammad-docker-compose',
            'VERSION'          : '-latest',
        }
