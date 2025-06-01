#!/usr/bin/python3

from os import listdir
from os.path import isfile, join

from Domain import Domain
from SubDomain import SubDomain
import config


class ServiceManager:
    """A docker-compose interface to manage web services"""
    # The top level directory
    rootDir = config.root_dir
    # A list of directories to ignore when looking for domains
    nonDomainDirs = ('bin', 'tmp')
    # All available top level domains
    domains: dict[str, Domain] = dict()

    def __init__(self):
        """Load all available domains"""
        self._currentDomain: Domain = None
        self._currentSubDomain: SubDomain = None

        # Load all available domains
        for f in listdir(self.rootDir):
            if f in self.nonDomainDirs or isfile(join(self.rootDir, f)):
                continue
            self.domain(f)

    @property
    def currentDomain(self):
        return self._currentDomain

    @currentDomain.setter
    def currentDomain(self, domain):
        self._currentDomain = domain
    
    @property
    def currentSubDomain(self):
        if None is self.currentDomain:
            return None
        return self._currentSubDomain
    
    @currentSubDomain.setter
    def currentSubDomain(self, subdomain):
        if None is self.currentDomain:
            return
        self._currentSubDomain = subdomain

    def domain(self, name):
        """Add a new or get an existing domain
        
        Args:
            name (string): The name of the domain
        
        Returns:
            Domain: The created domain
        """
        # Return existing domains
        if name in self.domains.keys():
            return self.domains[name]
        # Create a new domain
        domain = Domain(name, self.rootDir)
        self.domains[domain.__str__()] = domain
        return domain

    def deleteDomain(self, domain):
        """Delete a top level domain
        
        Args:
            name (Domain): The domain to delete
        """
        name = domain.__str__()
        # Delete the domain
        domain.delete()
        # Forget about the domain
        del self.domains[name]
