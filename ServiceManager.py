#!/usr/bin/python3

from os import listdir
from os.path import isfile, join

from Domain import Domain
from modules.WordPress import WordPress
from modules.Nextcloud import Nextcloud
from modules.Zammad import Zammad
import config


class ServiceManager:
    """A docker-compose interface to manage web services"""
    # The top level directory
    rootDir = config.root_dir
    # A list of directories to ignore when looking for domains
    nonDomainDirs = ('bin', 'tmp')
    # All available top level domains
    domains = dict()

    def __init__(self):
        """Load all available domains"""
        # Load all available domains
        for f in listdir(self.rootDir):
            if f in self.nonDomainDirs or isfile(join(self.rootDir, f)):
                continue
            self.domain(f)

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


if __name__ == '__main__':
    if __package__ is None:
        __package__ = "docker-compose"
    # Init manager
    manager = ServiceManager()
    # Create a new top level domain
    domain = manager.domain('example.com')
    # Within a top level domain, you can create subdomains
    # that can each hold one module (e.g. a WordPress instance)
    blogSubDomain = domain.subDomain('blog')    # This will create the subdomain "blog.example.com"
    blogWp = WordPress(blogSubDomain)
    # This starts all containers needed for WordPress and generates ssl certificates
    # and haproxy bindings. Afterwards the site can be accessed via "blog.example.com"
    blogWp.up()
    # To access the top level domain itself ("example.com"),
    # you have to create a subdomain for it as well
    mainSubDomain = domain.subDomain('example.com')
