#!/usr/bin/python3

import os

from .Module import Module


class Leantime(Module):
    def __init__(self, subDomain):
        """A Leantime installation

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['mysql', 'leantime', 'leantime/public_userfiles', 'leantime/userfiles', 'leantime/plugins', 'leantime/logs']
        super().__init__(subDomain)
        for dir in ('leantime/public_userfiles', 'leantime/userfiles', 'leantime/plugins', 'leantime/logs'):
            os.chown(os.path.join(self.subDomain.rootDir, dir), 1000, 1000)

    def _getCustomEnvVars(self) -> dict[str, str]:
        self.exposedPort = self.getFreePort()
        return {
            'HTTP_PORT'          : str(self.exposedPort),

            'PUID'                      : 1000,
            'PGID'                      : 1000,
            'LEAN_PORT'                 : 8080,
            'LEAN_APP_URL'              : 'https://' + str(self.subDomain),
            'LEAN_APP_DIR'              : '',
            'LEAN_DEBUG'                : 0,
            'MYSQL_ROOT_PASSWORD'       : self.password(),
            'LEAN_DB_HOST'              : 'db',
            'LEAN_DB_USER'              : 'lean',
            'LEAN_DB_PASSWORD'          : self.password(200),
            'LEAN_DB_DATABASE'          : 'leantime',
            'LEAN_DB_PORT'              : '3306',
            'LEAN_SESSION_PASSWORD'     : self.password(),
            'LEAN_SESSION_EXPIRATION'   : 28800,
            'LEAN_SESSION_SECURE'       : True,
            # Email
            'LEAN_EMAIL_RETURN': '',
            'LEAN_EMAIL_USE_SMTP': False,
            'LEAN_EMAIL_SMTP_HOSTS': '',
            'LEAN_EMAIL_SMTP_USERNAME': '',
            'LEAN_EMAIL_SMTP_PASSWORD': '',
            'LEAN_EMAIL_SMTP_SECURE': 'STARTTLS',
            'LEAN_EMAIL_SMTP_PORT': '587',
        }
