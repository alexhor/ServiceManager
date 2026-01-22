import base64
import os

from .Module import Module


class OAuthWebserver(Module):
    def __init__(self, subDomain):
        """A NGINX Webserver secured by OAuth2-Proxy

        Args:
            subDomain (SubDomain): The subdomain this module is installed on
        """
        self.requiredDirs = ['data']
        super().__init__(subDomain)

        print('Please update the environment variables with your OAuth2 provider configuration!')

    def _getCustomEnvVars(self) -> dict[str, str]:
        self.exposedPort = self.getFreePort()
        return {
            'OAUTH2_PROXY_PROVIDER'             : '<PROVIDER ID>',
            'OAUTH2_PROXY_PROVIDER_DISPLAY_NAME': '<PROVIDER DISPLAY NAME>',
            'OAUTH2_PROXY_CLIENT_ID'            : '<CLIENT ID HERE>',
            'OAUTH2_PROXY_CLIENT_SECRET'        : '<CLIENT SECRET HERE>',
            'OAUTH2_PROXY_LOGIN_URL'            : '<LOGIN URL>',
            'OAUTH2_PROXY_REDEEM_URL'           : '<TOKEN URL>',
            'OAUTH2_PROXY_VALIDATE_URL'         : '<VALIDATION URL>',
            'OAUTH2_PROXY_COOKIE_SECRET'        : base64.urlsafe_b64encode(os.urandom(32)).decode(),
        }
