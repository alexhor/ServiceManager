from os.path import join


class Proxy:
    other = 0
    haproxy = 1
    traefik = 2


used_proxy: Proxy = Proxy.traefik
proxy_network_name = 'proxy'
handle_ssl_certificates: bool = False

docker_compose_command: list[str] = ["docker", "compose"]
root_dir = join('/', 'srv', 'services')
