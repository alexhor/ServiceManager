#!/usr/bin/python3

from .Module import Module


class NoneModule(Module):
    def __init__(self, subDomain=None):
        """A dummy module
        
        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        pass

    def isNone(self):
        """States wether this is a proper module or not
        
        Returns:
            bool: Wether this is a proper module or not
        """
        return True

    def up(self):
        """Bring up this modules containers"""
        pass

    def down(self):
        """Stop all running containers"""
        pass

    def clean(self):
        """Delete all existing data"""
        pass

    def save(self, delete=True):
        """Save this module to the current subdomain
        
        Args:
            delete (bool): Obsolete, because there will never be a save file for this module
        """
        moduleFile = join(self.subDomain.rootDir, '.module')
        if isfile(moduleFile):
            remove(moduleFile)
