#!/usr/bin/python3

from os import listdir, makedirs
from os.path import isfile, isdir, join
from shutil import rmtree

from SubDomain import SubDomain

class Domain:
    """A top level domain"""
    # A list of all default folders
    defaultFolderList = ('',)
    # A list of directories to ignore when looking for subdomains
    nonDomainDirs = ('bin', 'tmp')

    """Make sure every required folder and file for this domain exists
    
    Args:
        name (string): The domain name
        rootDir (string): The root directory all top level domains are in
    """
    def __init__(self, name: str, rootDir: str):
        self.name: str = name
        # This domains top directory
        self.rootDir: str = join(rootDir, self.name)
        # Make sure top level directory exists
        if not isdir(self.rootDir):
            makedirs(self.rootDir)
        # Make sure the default folders exist
        for folderName in self.defaultFolderList:
            folderDir = join(self.rootDir, folderName)
            if not isdir(folderDir):
                makedirs(folderDir)
        self.loadSubDomains()

    def loadSubDomains(self):
        """Get all existing subdomains"""
        self.subDomains = dict()
        for domainName in listdir(self.rootDir):
            if domainName in self.nonDomainDirs or isfile(join(self.rootDir, domainName)):
                continue
            # Only allow real subdomains
            if domainName[-1 * len(self.name):] != self.name:
                continue
            # Strip the root domain name
            if domainName != self.name:
                domainName = domainName[:-1 * len(self.name) - 1]
            self.subDomain(domainName)
        return self.subDomains

    def __repr__(self):
        return self.name

    def subDomain(self, name):
        """Add a new or get an existing subdomain
        
        Args:
            name (string): The name of the subdomain
        
        Returns:
            SubDomain: The created subdomain
        """
        if name != self.name:
            name = name + '.' + self.name
        # Return existing subdomains
        if name in self.subDomains.keys():
            return self.subDomains[name]
        # Create a new subdomain
        subDomain = SubDomain(name, self)
        self.subDomains[subDomain.__str__()] = subDomain
        return subDomain

    def deleteSubDomain(self, subDomain):
        """Delete an existing subdomain
        
        Args:
            name (subDomain): The subdomain to delete
        """
        name = str(subDomain)
        # Delete the subdomain
        subDomain.delete()
        # Forget about the subdomain
        del self.subDomains[name]

    def delete(self):
        """Delete this top level domain"""
        subDomainList = list(self.subDomains.values())
        # Delete all subdomains
        for subDomain in subDomainList:
            self.deleteSubDomain(subDomain)
        # Delete the top level domain itself
        rmtree(self.rootDir, ignore_errors=True)
