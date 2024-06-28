#!/usr/bin/python3

from os import makedirs
from os.path import isfile, isdir, join
from shutil import rmtree
from subprocess import call

from modules.ModuleLoader import ModuleLoader
from modules.NoneModule import NoneModule
import config

class SubDomain:
    """A domain that can host a module"""
    # A list of all default folders
    defaultFolderList = ('httpdocs',)
    # A list of directories to ignore when looking for subdomains
    nonDomainDirs = ('bin', 'tmp')
    # Config file location for haproxy
    _haproxyConfigFile = join('/', 'etc', 'haproxy', 'haproxy.cfg')

    def __init__(self, name, topLevelDomain):
        """Make sure every required folder and file for this domain exists
        
        Args:
            name (string): The domains name
        """
        self.name = name
        self.topLevelDomain = topLevelDomain
        # This domains top directory
        self.rootDir = join(self.topLevelDomain.rootDir, self.name)
        # Make sure the domains directory exists
        if not isdir(self.rootDir):
            makedirs(self.rootDir)
        # Make sure an ssl certificate for this subdomain exists
        self._setupSsl()
        # Load currently active module if one exists
        self.activeModule = ModuleLoader.load(subDomain=self)

    def __repr__(self):
        return self.name

    def addModule(self, module):
        """Add a module to this domain
        
        Args:
            module (Module): The module to add
        """
        # Remove any currently active module
        self.deleteModule()
        # Add new module
        self.activeModule = module

    def deleteModule(self):
        """Delete the domains module if exists"""
        self.activeModule.clean()
        self.activeModule = NoneModule()

    def delete(self):
        """Delete this subdomain"""
        self.deleteModule()
        rmtree(self.rootDir, ignore_errors=True)

    def haproxyConfig(self, delete = False):
        """Configure haproxy to redirect to this domains module
        
        Args:
            delete (bool): Delete or add the given rule
        """
        if config.Proxy.haproxy != config.used_proxy:
            return
        # Adding rules is only allowed with a valid module
        if not delete and self.activeModule.isNone():
            return
        outputBuffer = ''
        aclName = self.name.replace('.', '-')

        # Compose haproxy.cfg
        with open(self._haproxyConfigFile, 'r+') as haproxyCfg:
            isBackend = False
            isFrontend = False
            prevLine = ''

            for line in haproxyCfg:
                lineStrip = line.strip()
                # New backend started
                if lineStrip[:8] == 'backend ':
                    # Check if this is the correct block
                    isFrontend = False
                    isBackend = lineStrip[8:] == aclName
                    # Delete backend by default
                    if isBackend:
                        prevLine = line
                        continue
                # New frontend started
                elif lineStrip[:9] == 'frontend ':
                    isBackend = False
                    # Check if this is the correct block
                    isFrontend = lineStrip[9:] == 'http'
                # Special handling for backend
                elif isBackend:
                    # Delete backend by default
                    if line != '# END OF SERVICES\n':
                        prevLine = line
                        continue
                # Special handling for frontend
                elif isFrontend:
                    # Make sure the subdomains ssl certificate is beeing loaded
                    if '\tbind *:80\n' == prevLine:
                        certString = ' crt ' + self._sslCertificateFile
                        # Add ssl binding if it is missing
                        if 'bind *:443 ssl ' != lineStrip[:15]:
                            outputBuffer += '\tbind *:443 ssl' + certString + '\n'
                        elif delete:
                            # Delete the domains ssl certificate and if it is the last certificate, delete the whole bind
                            if '\tbind *:443 ssl' + certString + '\n' != line:
                                outputBuffer += line.replace(certString, '')
                            # Remove the old line
                            prevLine = line
                            continue
                        elif certString not in line:
                            # Add the domains ssl certificate
                            outputBuffer += '\t' + lineStrip + certString + '\n'
                            # Remove the old line
                            prevLine = line
                            continue
                    # Delete old server lines
                    elif lineStrip[:len('acl ' + aclName) + 1] == 'acl ' + aclName + ' ' \
                            or lineStrip[:len('use_backend ' + aclName)] == 'use_backend ' + aclName:
                        prevLine = line
                        continue
                    # Add new server lines at the end
                    elif not delete and line == '\t# END OF SERVICES\n':
                        outputBuffer += '\tacl ' + aclName + ' req.hdr(Host) ' + self.name + '\n'
                        outputBuffer += '\tuse_backend ' + aclName + ' if ' + aclName + '\n'
                # Add a new backend rule if it doesn't exist
                elif line == '# END OF SERVICES\n' and not delete:
                    outputBuffer += 'backend ' + aclName + '\n' \
                                    + '\toption httpclose\n' \
                                    + '\toption forwardfor\n' \
                                    + '\thttp-request set-header X-Forwarded-Port %[dst_port]\n' \
                                    + '\thttp-request add-header X-Forwarded-Proto https if { ssl_fc }\n' \
                                    + '\tserver ' + self.activeModule.name + ' 127.0.0.1:' + str(self.activeModule.exposedPort) + ' check fall 3 rise 2\n'
                # Write accepted lines
                outputBuffer += line
                prevLine = line
        # Write new haproxy.cfg
        with open(self._haproxyConfigFile, 'w') as haproxyCfg:
            haproxyCfg.write(outputBuffer)
        # Load new configuration
        call(['systemctl', 'reload', 'haproxy'])

    def _setupSsl(self, forceRenewal = False):
        """Setup this subdomain to allow connections over https
        
        Args:
            forceRenewal (bool): If the renewal should be forced
        """
        if not config.handle_ssl_certificates:
            return
        certFolder = join('/', 'etc', 'ssl')
        self._sslCertificateFile = join(certFolder, self.name + '/cert.pem')
        if isfile(self._sslCertificateFile):
            # Nothing to do here if the certificate already exists and renewal is not forced
            if not forceRenewal:
                return
            # Forcefully renew this subdomains certificate
            else:
                pass # // TODO: implement forced renewal
        # Request a certificate for the first time
        call(['certbot', 'certonly', '--standalone', '-d', self.name, '--non-interactive', '--agree-tos',
                '--email', 'alexander@h-software.de', '--http-01-port=8888'])
        if not isdir(certFolder):
            makedirs(certFolder)
        # Create combined certificate file for haproxy to use
        keyDir = join('/', 'etc', 'letsencrypt', 'live', self.name)
        with open(self._sslCertificateFile, 'w') as certFile:
            with open(join(keyDir, 'fullchain.pem'), 'r') as fullchain:
                certFile.write(fullchain.read())
            with open(join(keyDir, 'privkey.pem'), 'r') as privkey:
                certFile.write(privkey.read())
