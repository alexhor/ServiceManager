#!/usr/bin/python3

from os import chown, makedirs, remove
from os.path import exists, isfile, isdir, join
import secrets, string, re
from socketserver import TCPServer
from shutil import rmtree
from subprocess import call

import config


class Module:
    # A temporary config file location
    tmpConfigFile = 'docker-compose.yml'
    # The local port exposed by a http server
    exposedPort = None

    def __init__(self, subDomain):
        """An abstract base module
        
        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.name = type(self).__name__
        self.subDomain = subDomain
        self.envFile = join(self.subDomain.rootDir, '.env')
        self.moduleTemplate = join('modules', 'module-templates', self.name + '.yml')
        # Create all required dirs
        for dirName in self.requiredDirs:
            folderPath = join(self.subDomain.rootDir, dirName)
            if not exists(folderPath):
                makedirs(folderPath)
                # Set permissions for docker
                chown(folderPath, 1000, 1000)
        # Get the http port if it exists
        self.envFileDict = self.envFileToDict()
        if 'HTTP_PORT' in self.envFileDict.keys():
            self.exposedPort = self.envFileDict['HTTP_PORT']

    def __repr__(self):
        return type(self).__name__

    @staticmethod
    def password(length = 255):
        """Generate a secure password
        
        Args:
            length (int): The passwords length
        
        Returns:
            string: A secure password
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(length))

    @staticmethod
    def getFreePort():
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
        return self.fileToDict(self.envFile)

    @staticmethod
    def fileToDict(filePath):
        """Get a dictionary representation of a file
        
        Args:
            filePath (string): Path to the file to convert
        Returns:
            dict: The converted file
        """
        if not isfile(filePath):
            return dict()
        envVars = dict()
        with open(filePath, 'r') as file:
            for line in file:
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
        call(config.docker_compose_command + ['-f', self.tmpConfigFile, 'up', '-d'])
        # Configure haproxy
        self.subDomain.haproxyConfig()
        self.save()

    def down(self):
        """Stop all running containers"""
        self._prepareTemplateFile()
        call(config.docker_compose_command + ['-f', self.tmpConfigFile, 'down'])
        # Configure haproxy
        self.subDomain.haproxyConfig(True)
        self.save()

    def clean(self):
        """Delete all existing data"""
        self.down()
        call(config.docker_compose_command + ['-f', self.tmpConfigFile, 'rm'])
        remove(self.envFile)
        # Delete all required dirs
        for dirName in self.requiredDirs:
            dirPath=join(self.subDomain.rootDir, dirName)
            if isdir(dirPath):
                rmtree(dirPath)
        self.save(True)

    def isNone(self):
        """States wether this is a proper module or not
        
        Returns:
            bool: Wether this is a proper module or not
        """
        return False

    def save(self, delete=False):
        """Save this module to the current subdomain
        
        Args:
            delete (bool): Wether the current module should be deleted"""
        moduleFile = join(self.subDomain.rootDir, '.module')
        if delete:
            if isfile(moduleFile):
                remove(moduleFile)
        else:
            with open(moduleFile, 'w') as file:
                file.write('MODULE_NAME=' + self.name + '\n')

    def getContainers(self) -> list[str]:
        """Get a string list of all containers in this module"""
        self._prepareTemplateFile()
        with open(self.moduleTemplate, 'r') as configTemplateFile:
            configFileContent = configTemplateFile.read()
        containerMatches = re.findall(r"\n\s+container_name:\s+(?:\${DOMAIN_ESCAPED})_(.+)\s*\n", configFileContent)
        return containerMatches

    def showContainerLogs(self, containerName):
        if containerName not in self.getContainers():
            print('Invalid container name')
            return
        envVars = self.envFileToDict()
        fullContainerName = envVars['DOMAIN_ESCAPED'] + '_' + containerName
        try:
            call(['docker', 'logs', '-f', fullContainerName])
        except KeyboardInterrupt:
            print()
            print('Log output ended')

    def runContainerCmd(self, containerName, command="/bin/bash"):
        if containerName not in self.getContainers():
            print('Invalid container name')
            return
        envVars = self.envFileToDict()
        fullContainerName = envVars['DOMAIN_ESCAPED'] + '_' + containerName
        try:
            call(['docker', 'exec', '-it', fullContainerName, command])
        except KeyboardInterrupt:
            print()
            print('Container command ended')
