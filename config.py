from enum import Enum
from os.path import join

class Proxy:
    other   = 0
    haproxy = 1
    traefik = 2

used_proxy: Proxy = Proxy.traefik
handle_ssl_certificates: bool = False

docker_compose_command: list[str] = ["docker", "compose"]
root_dir = join('/', 'var', 'www', 'services')

