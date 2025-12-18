#!/usr/bin/python3
import os
import shutil
import subprocess
from os.path import join, exists
from pathlib import Path

from .Module import Module


class Registry(Module):
    """
    This module contains a self-hosted container registry and a "builder" container,
    which rebuilds custom images daily and uploads them to the attached registry.
    """
    envKeyUser = 'REGISTRY_BUILDER_USER'
    envKeyPass = 'REGISTRY_BUILDER_PASS'

    def __init__(self, subDomain):
        self.requiredDirs = ['builder', 'registry']
        super().__init__(subDomain)

        self.htpasswdFile = join(self.subDomain.rootDir, 'htpasswd')

        if not exists(join(self.subDomain.rootDir, 'builder')):
            subprocess.call(['git', 'clone', 'https://github.com/JonFStr/ContainerBuilder', 'builder'],
                            cwd=self.subDomain.rootDir)
            # Copy default crontab
            shutil.copy(join(self.subDomain.rootDir, 'builder', 'crontab.dist'),
                        join(self.subDomain.rootDir, 'builder', 'crontab'))

        # Save passwords to htpasswd
        if not exists(self.htpasswdFile):
            Path(self.htpasswdFile).touch()
            subprocess.call(
                ['htpasswd', '-Bb', self.htpasswdFile, self.envVars[self.envKeyUser], self.envVars[self.envKeyPass]])
            registryPwd = self.password(255)
            subprocess.call(['htpasswd', '-Bb', self.htpasswdFile, 'registry', registryPwd])
            print('The following users were saved to $DOMAIN_PATH/htpasswd:')
            print(f'Username: {self.envVars[self.envKeyUser]} --- Password: {self.envVars[self.envKeyPass]}')
            print(f'Username: registry --- Password: {registryPwd}')
            print('Use `htpasswd -Bb $DOMAIN_PATH/htpasswd <user> <password>` to add / update credentials.')

    def _getCustomEnvVars(self) -> dict[str, str]:
        return {
            self.envKeyUser: 'builder',
            self.envKeyPass: self.password(255),
        }

    def clean(self):
        super().clean()
        os.remove(join(self.htpasswdFile))
