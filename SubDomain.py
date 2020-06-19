#!/usr/bin/python3

from os import makedirs
from os.path import isfile, isdir, join
from shutil import rmtree
from subprocess import call

class SubDomain:
    """A domain that can host a module"""
    # A list of all default folders
    defaultFolderList = ('httpdocs',)
    # A list of directories to ignore when looking for subdomains
    nonDomainDirs = ('bin', 'tmp')
    # The currently active module
    activeModule = None
    # Config file location for haproxy
    _haproxyConfigFile = join('/', 'etc', 'haproxy', 'haproxy.cfg')

    """Make sure every required folder and file for this domain exists
    
    Args:
        name (string): The domains name
        rootDir (string): The main domains directory
    """
    def __init__(self, name, rootDir, topLevelDomain):
        self.name = name
        self.topLevelDomain = topLevelDomain
        # This domains top directory
        self.rootDir = join(rootDir, self.name)
        # Make sure the domains directory exists
        if not isdir(self.rootDir):
            makedirs(self.rootDir)
        # Make sure an ssl certificate for this subdomain exists
        self._setupSsl()
        # // TODO: load module if one exists

    def __repr__(self):
        return self.name

    def AddModule(self, module):
        """Add a module to this domain
        
        Args:
            module (Module): The module to add
        """
        # Remove any currently active module
        self.deleteModule()
        # Add new module
        self.activeModule = module
        # // TODO: save module for later

    def deleteModule(self):
        """Delete the domains module if exists"""
        self.haproxyConfig(delete=True)
        if self.activeModule is not None:
            self.activeModule.clean()
        self.activeModule = None

    def delete(self):
        """Delete this subdomain"""
        self.deleteModule()
        rmtree(self.rootDir, ignore_errors=True)

    def haproxyConfig(self, delete = False):
        """Configure haproxy to redirect to this domains module
        
        Args:
            delete (bool): Delete or add the given rule
        """
        # Adding rules is only allowed with a valid module
        if not delete and self.activeModule is None:
            return
        outputBuffer = ''
        aclName = self.name.replace('.', '-')

        # compose haproxy.cfg
        with open(self._haproxyConfigFile, 'r+') as haproxyCfg:
            isBackend = False
            isFrontend = False
            prevLine = ''

            for line in haproxyCfg:
                lineStrip = line.strip()
                # new backend started
                if lineStrip[:8] == 'backend ':
                    # check if this is the correct block
                    isFrontend = False
                    isBackend = lineStrip[8:] == aclName
                    # Delete backend by default
                    if isBackend:
                        prevLine = line
                        continue
                # new frontend started
                elif lineStrip[:9] == 'frontend ':
                    isBackend = False
                    # check if this is the correct block
                    isFrontend = lineStrip[9:] == 'http'
                # special handling for backend
                elif isBackend:
                    # Delete backend by default
                    prevLine = line
                    continue
                # special handling for frontend
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
                            outputBuffer += line + certString + '\n'
                            # Remove the old line
                            prevLine = line
                            continue
                    # delete old server lines
                    elif lineStrip[:len('acl ' + aclName) + 1] == 'acl ' + aclName + ' ' \
                            or lineStrip[:len('use_backend ' + aclName)] == 'use_backend ' + aclName:
                        prevLine = line
                        continue
                    # add new server lines at the end
                    elif not delete and line == '\t# END OF SERVICES\n':
                        if prevLine != '\t# SERVICES\n':
                            outputBuffer += '\n'
                        outputBuffer += '\tacl ' + aclName + ' req.hdr(Host) ' + self.name + '\n'
                        outputBuffer += '\tuse_backend ' + aclName + ' if ' + aclName + '\n'
                # add a new backend rule if it doesn't exist
                elif line == '# END OF SERVICES\n' and not delete:
                    if prevLine != '# SERVICES\n':
                        outputBuffer += '\n'
                    outputBuffer += 'backend ' + aclName + '\n' \
                                    + '\toption httpclose\n' \
                                    + '\toption forwardfor\n' \
                                    + '\thttp-request set-header X-Forwarded-Port %[dst_port]\n' \
                                    + '\thttp-request add-header X-Forwarded-Proto https if { ssl_fc }\n' \
                                    + '\tserver ' + self.activeModule.name + ' 127.0.0.1:' + self.activeModule.exposedPort + ' check fall 3 rise 2\n'
                # write accepted lines
                outputBuffer += line
                prevLine = line
        # write new haproxy.cfg
        #print(outputBuffer)
        with open(self._haproxyConfigFile, 'w') as haproxyCfg:
            haproxyCfg.write(outputBuffer)
        # Load new configuration
        call(['systemctl', 'reload', 'haproxy'])

    def _setupSsl(self, forceRenewal = False):
        """Setup this subdomain to allow connections over https
        
        Args:
            forceRenewal (bool): If the renewal should be forced
        """
        certFolder = join('/', 'etc', 'ssl', self.topLevelDomain.name)
        self._sslCertificateFile = join(certFolder, self.name + '.pem')
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
        makedirs(certFolder)
        # Create combined certificate file for haproxy to use
        keyDir = join('/', 'etc', 'letsencrypt', 'live', self.name)
        with open(self._sslCertificateFile, 'w') as certFile:
            with open(join(keyDir, 'fullchain.pem'), 'r') as fullchain:
                certFile.write(fullchain.read())
            with open(join(keyDir, 'privkey.pem'), 'r') as privkey:
                certFile.write(privkey.read())


# // TODO: configure haproxy
# // TODO: configure letsencrypt
