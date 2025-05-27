#!/usr/bin/python3

from os import makedirs
from os.path import isfile, isdir
from subprocess import run
from distutils.dir_util import copy_tree

from .Module import Module


class Odoo(Module):
    def __init__(self, subDomain):
        """A odoo instance with Postgres

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['postgresql', 'odoo', 'odoo/addons', 'odoo/etc', 'odoo/lib']
        super().__init__(subDomain)
        configFilePath = self.subDomain.rootDir + '/odoo/etc/odoo.conf'
        if not isfile(configFilePath):
            with open(configFilePath, 'w') as configFile:
                configFile.write('[options]\n')
                configFile.write('addons_path = /mnt/extra-addons\n')
                configFile.write('data_dir = /var/lib/odoo\n')
                configFile.write('\n')

    def _createEnvFile(self):
        """Put all requried parameters into an .env file in the subdomains root directory"""
        self.exposedPort = self.getFreePort()
        self.livechatPort = self.getFreePort()
        with open(self.envFile, 'w') as envFile:
            envFile.write('DOMAIN=' + str(self.subDomain) + '\n')
            envFile.write('DOMAIN_ESCAPED=' + str(self.subDomain).replace('.', '-') + '\n')
            envFile.write('HTTP_PORT=' + str(self.exposedPort) + '\n')
            envFile.write('DOMAIN_PATH=' + self.subDomain.rootDir + '\n')
            envFile.write('POSTGRES_PASSWORD=' + self.password() + '\n')
            envFile.write('LIVECHAT_PORT=' + str(self.livechatPort) + '\n')
