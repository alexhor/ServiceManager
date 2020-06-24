#!/usr/bin/python3

from os import makedirs, remove
from os.path import exists, isfile, join
import secrets
import string
from socketserver import TCPServer
from shutil import copy, rmtree
from subprocess import call

class Module:
    # A temporary config file location
    tmpConfigFile = 'docker-compose.yml'
    # The local port exposed by a http server
    exposedPort = None

    def __init__(self, subDomain, moduleName):
        """An abstract base module
        
        Args:
            subDomain (SubDomain): The subdomain this module is installed on
            moduleName (string): Name of this module
        """
        self.name = moduleName
        self.subDomain = subDomain
        self.envFile = join(self.subDomain.rootDir, '.env')
        self.moduleTemplate = join('modules', 'module-templates', self.name + '.yml')
        # Create all required dirs
        for dirName in self.requiredDirs:
            folderPath = join(self.subDomain.rootDir, dirName)
            if not exists(folderPath):
                makedirs(folderPath)
        # Tell the subdomain about this module
        self.subDomain.AddModule(self)
        # Get the http port if it exists
        self.envFileDict = self.envFileToDict()
        if 'HTTP_PORT' in self.envFileDict.keys():
            self.exposedPort = self.envFileDict['HTTP_PORT']

    def password(self, length = 255):
        """Generate a secure password
        
        Args:
            length (int): The passwords length
        
        Returns:
            string: A secure password
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(length))

    def getFreePort(self):
        """Get a port available for binding
        
        Returns:
            int: A free port
        """
        with TCPServer(('localhost', 0), None) as s:
            return s.server_address[1]

    def _createEnvFile(self):
        """Put all requried parameters into an .env file in the subdomains root directory"""
        # This has to be done by the individual modules
        pass

    def envFileToDict(self):
        """Get a dictionary representation of this modules env file
        
        Returns:
            dict: The converted env file
        """
        if not isfile(self.envFile):
            return dict()
        envVars = dict()
        with open(self.envFile, 'r') as envFile:
            for line in envFile:
                splitLine = line.strip().split('=', 1)
                # Skip invalid lines
                if len(splitLine) != 2:
                    continue
                envVars[splitLine[0]] = splitLine[1]
        return envVars

    def _prepareTemplateFile(self):
        """Get a template file and fill in any variables"""
        # Make sure an env file exists
        if not isfile(self.envFile):
            self._createEnvFile()
        envVars = self.envFileToDict()
        configFileContent = ''
        # Get the config template file
        with open(self.moduleTemplate, 'r') as configTemplateFile:
            configFileContent = configTemplateFile.read()
        # Replace template variables
        for key, value in envVars.items():
            configFileContent = configFileContent.replace('${' + key + '}', value)
        # Write final config file
        with open(self.tmpConfigFile, 'w') as configFile:
            configFile.write(configFileContent)

    def up(self):
        """Bring up this modules containers"""
        self._prepareTemplateFile()
        # Bring up containers
        call(['docker-compose', '-f', self.tmpConfigFile, 'up', '-d'])
        # Configure haproxy
        self.subDomain.haproxyConfig()

    def down(self):
        """Stop all running containers"""
        self._prepareTemplateFile()
        call(['docker-compose', '-f', self.tmpConfigFile, 'down'])
        # Configure haproxy
        self.subDomain.haproxyConfig(True)

    def clean(self):
        """Delete all existing data"""
        self.down()
        call(['docker-compose', '-f', self.tmpConfigFile, 'rm'])
        remove(self.envFile)
        # Delete all required dirs
        for dirName in self.requiredDirs:
            rmtree(join(self.subDomain.rootDir, dirName))
