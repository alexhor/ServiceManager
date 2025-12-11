# ServiceManager
Manage web services with docker-compose and haproxy

Warning: This programm is under heavy development and probably not very stable

## IMPORTANT: Update to v2.0
The new update makes use of `docker compose` for a lot of the name generating & variable expansion.
Therefore containers started by old versions of this manager will not be recognized by the new one.

To update, simply run `module down` for every subdomain **from the old version**,
then perform the upgrade and run `module up` for every subdomain.  

## Usage
Start the command line interface
```
python CLI.py
```
***
For a full list of commands check the [Wiki](https://github.com/alexhor/ServiceManager/wiki/CLI-command-reference)
***

Create a new or select an existing top level domain
```python
ServiceManager>select domain example.com
selected domain "example.com"
```
After selecting a domain, get all current subdomains for it
```python
ServiceManager>list subdomain
avaibale subdomains:
    blog.example.com
    nextcloud.example.com
```
Create a new or select an existing subdomain, add a module to it and bring that module up
```python
ServiceManager>create sd blog
selected subdomain "blog.example.com"
ServiceManager>create md WordPress
created module "WordPress"
ServiceManager>up md
Creating network "bin_blog-example-com" with the default driver
Creating blog-example-com_mysql ... done
Creating blog-example-com_wordpress ... done
module "WordPress" is coming up
```

## Usaging the ServiceManager directly
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


## Dependencies
  * Docker
  * Docker-Compose
  * haproxy
  * certbot
