#!/usr/bin/python3
from .Module import Module
from .MySql import MySql


class StaticWeb(MySql, Module):
    def __init__(self, subDomain):
        """An nginx server for static web content.

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['src']
        super().__init__(subDomain)
