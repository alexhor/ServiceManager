#!/usr/bin/python3

from os.path import isfile

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

    def _getCustomEnvVars(self) -> dict[str, str]:
        self.exposedPort = self.getFreePort()
        self.livechatPort = self.getFreePort()
        return {
            'HTTP_PORT'        : str(self.exposedPort),
            'POSTGRES_PASSWORD': self.password(),
            'LIVECHAT_PORT'    : str(self.livechatPort),
        }
