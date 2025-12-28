#!/usr/bin/python3
from os.path import join
from pathlib import Path

from .Module import Module


class WordPress(Module):
    def __init__(self, subDomain):
        """A WordPress installation

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['mariadb', 'wordpress']
        super().__init__(subDomain)

    def up(self):
        # Create php.ini file - otherwise, docker compose will make the mount a directory
        Path(join(self.subDomain.rootDir, 'php.ini')).touch()
        # Call super
        super().up()

    def _getCustomEnvVars(self) -> dict[str, str]:
        self.exposedPort = self.getFreePort()
        return {
            'MARIADB_PASSWORD'     : self.password(),
            'MARIADB_ROOT_PASSWORD': self.password(),
            'SMTP_HOST'            : 'localhost',
            'SMTP_USERNAME'        : 'root@localhost',
            'SMTP_PASSWORD'        : 'thisisaplaceholder',
            'SMTP_FROM'            : 'root@localhost',
            'SMTP_FROM_NAME'       : 'WordPress',
        }
