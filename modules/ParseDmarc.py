#!/usr/bin/python3

import os
import json

from .Module import Module


class ParseDmarc(Module):
    def __init__(self, subDomain):
        """A ParseDmarc installation

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['data']
        super().__init__(subDomain)
        self._configFileLocation = os.path.join(self.subDomain.rootDir, 'config.json')
        if not os.path.exists(self._configFileLocation):
            config = {
                "imap": {
                    "host": "",
                    "port": 993,
                    "username": "",
                    "password": "",
                    "use_tls": True
                },
                "database": {
                    "path": "/data/db.sqlite"
                },
                "server": {
                    "port": 8080,
                    "host": "0.0.0.0"
                }
            }
            with open(self._configFileLocation, 'w') as configFile:
                json.dump(config, configFile, indent=4)

    def clean(self):
        """Delete all existing data"""
        super().clean()
        os.remove(self._configFileLocation)

