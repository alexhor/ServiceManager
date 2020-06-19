# ServiceManager
Manage web services with docker-compose and haproxy

Warning: This programm is under heavy development and probably not very stable

## Usage
```python
from ServiceManager import ServiceManager
# Init manager
manager = ServiceManager()
# Create a new top level domain
domain = manager.domain('example.com')
```
```python
# Within a top level domain, you can create subdomains
# that can each hold one module (e.g. a WordPress instance)
blogSubDomain = domain.subDomain('blog')    # This will create the subdomain "blog.example.com"
blogWp = WordPress(blogSubDomain)
# This starts all containers needed for WordPress and generates ssl certificates
# and haproxy bindings. Afterwards the site can be accessed via "blog.example.com"
blogWp.up()
```
```python
# To access the top level domain itself ("example.com"),
# you have to create a subdomain for it as well
mainSubDomain = domain.subDomain('example.com')
```
A cli will follow in the near future

## Dependencies
  * Docker
  * Docker-Compose
  * haproxy
  * certbot
