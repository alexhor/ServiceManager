#!/usr/bin/python3
import secrets
import shutil
import string
from os import chown, makedirs, remove
from os.path import exists, isfile, isdir, join, dirname
from shutil import rmtree
from socketserver import TCPServer
from subprocess import call, run, CompletedProcess

import config


class Module:
    """
    Abstract module base
    """
    # Location of this module's generated compose file
    composeFile: str
    # The local port exposed by a http server
    exposedPort = None

    def __init__(self, subDomain):
        """
        Initiate a new Module instance.

        This creates the directories required for this module, as well as the `.env`-file

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.name = type(self).__name__
        self.subDomain = subDomain
        self.envFile = join(self.subDomain.rootDir, '.env')
        self.composeFile = join(self.subDomain.rootDir, 'docker-compose.yml')
        self.moduleTemplate = join(dirname(__file__), 'module-templates', self.name + '.yml')
        # Create all required dirs
        for dirName in self.requiredDirs:
            folderPath = join(self.subDomain.rootDir, dirName)
            if not exists(folderPath):
                makedirs(folderPath)
                # Set permissions for docker
                chown(folderPath, 1000, 1000)

        # Load & Update environment variables on startup
        self.envVars = self._createOrUpdateEnvFile()

        # Get the http port if it exists
        if 'HTTP_PORT' in self.envVars.keys():
            self.exposedPort = self.envVars['HTTP_PORT']

    def __repr__(self):
        return type(self).__name__

    @staticmethod
    def password(length=255):
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

    def _createOrUpdateEnvFile(self) -> dict[str, str]:
        """Put all required parameters into an .env file in the subdomains root directory, adding new values if unset

        Returns:
            dict[str, str]: The variables committed to file
        """
        # TODO rename URL & PATH to MODULE_URL & MODULE_ROOT for future path-prefix modules
        default_vars = {
            'DOMAIN'              : str(self.subDomain),
            'DOMAIN_ESCAPED'      : self._domain_escaped,
            'DOMAIN_URL'          : 'https://' + str(self.subDomain),
            'DOMAIN_PATH'         : self.subDomain.rootDir,
            'COMPOSE_PROJECT_NAME': '${DOMAIN_ESCAPED}',
            'PROXY_NETWORK_NAME'  : config.proxy_network_name,
        }
        # Keys in the latter dictionary take precedence -> subclass method can override default variables
        combined_vars = default_vars | self._getCustomEnvVars()

        # If file already exists, update new values only
        if isfile(self.envFile):
            # Same precedence applies -> values from file take precedence
            combined_vars = combined_vars | Module.fileToDict(self.envFile)

        # Save combined variables to file
        with open(self.envFile, 'w') as envFile:
            envFile.writelines(f'{name}={value}\n' for (name, value) in combined_vars.items())

        return combined_vars

    def _getCustomEnvVars(self) -> dict[str, str]:
        """
        Obtain custom environment variables for this module.

        Subclasses should override this method to add environment variables to the module's configuration.

        The following variables are created by default:

        - `DOMAIN`: FQDN of the subdomain this module is added to
        - `DOMAIN_ESCAPED`: FQDN with dashes instead of dots separating levels
        - `MODULE_URL`: URL to the module's content root
        - `MODULE_PATH`: File system path to the module's content root on the *host disk*

        Returns:
            A dictionary of additional <variable name> : <value> mappings.

        """
        return dict()

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

    def _generateComposeFile(self):
        """Generate the compose file for this module and save it to the module directory."""
        # Since there are no moving parts in the templates, a simple copy is sufficient
        shutil.copy(self.moduleTemplate, self.composeFile)

    def up(self):
        """Bring up this modules containers"""
        self._generateComposeFile()
        # Bring up containers
        self._call_compose('up', '-d')
        # Configure haproxy
        self.subDomain.haproxyConfig()
        self.save()

    def down(self):
        """Stop all running containers"""
        self._generateComposeFile()
        self._call_compose('down')
        # Configure haproxy
        self.subDomain.haproxyConfig(True)
        self.save()

    def clean(self):
        """Delete all existing data"""
        self.down()
        self._call_compose('rm', '-v')
        remove(self.envFile)
        remove(self.composeFile)
        # Delete all required dirs
        for dirName in self.requiredDirs:
            dirPath = join(self.subDomain.rootDir, dirName)
            if isdir(dirPath):
                rmtree(dirPath)
        self.save(delete=True)

    def isNone(self):
        """States whether this is a proper module or not"""
        return False

    def save(self, *, delete=False):
        """Save this module to the current subdomain

        Args:
            delete (bool): Whether the current module should be deleted"""
        moduleFile = join(self.subDomain.rootDir, '.module')
        if delete:
            if isfile(moduleFile):
                remove(moduleFile)
        else:
            with open(moduleFile, 'w') as file:
                file.write('MODULE_NAME=' + self.name + '\n')

    def getContainers(self) -> list[str]:
        """Get a string list of all running containers in this module"""
        self._generateComposeFile()
        out_services: str = self._run_compose('ps', '--services').stdout
        return out_services.splitlines()

    def showContainerLogs(self, containerName):
        if containerName not in self.getContainers():
            print('Invalid service name')
            return
        try:
            self._call_compose('logs', '-f', containerName)
        except KeyboardInterrupt:
            print()
            print('Log output ended')

    def runContainerCmd(self, containerName, cmd_binary="/bin/bash", *args):
        if containerName not in self.getContainers():
            print('Invalid service name')
            return
        try:
            self._call_compose('exec', '-it', containerName, cmd_binary, *args)
        except KeyboardInterrupt:
            print()
            print('Container command ended')

    def _call_compose(self, *args) -> int:
        """
        Execute docker compose with the given arguments.

        Args:
            *args (str): Compose command to execute. Passed to `_compile_compose_args`

        Returns:
            int: Exit code of the subprocess
        """
        return call(self._compile_compose_args(*args))

    def _run_compose(self, *args) -> CompletedProcess:
        """
        Execute docker compose with the given arguments, capturing text _(i.e. encoded)_ output

        Args:
            *args (str): Compose command to execute. Passed to `_compile_compose_args`

        Returns:
            CompletedProcess: Exit code of the subprocess
        """
        return run(self._compile_compose_args(*args), capture_output=True, text=True)

    def _compile_compose_args(self, *args) -> list[str]:
        """
        Compile arguments for a `docker compose` call into a single list for e.g. `subprocess.call`.

        This function takes the argument list specified in config.py,
        appends the generated `-f docker-compose.yml` and then all parameters passes to this function.

        Args:
            *args (str): Compose command to execute
        """
        return config.docker_compose_command + ['-f', self.composeFile] + list(args)

    @property
    def _domain_escaped(self) -> str:
        """Escaped subdomain name"""
        return str(self.subDomain).replace('.', '-')
