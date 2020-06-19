all: setup docker-up-dev

setup:
	mkdir -p wordpress mysql

clean: docker-down
	docker-compose rm
	rm -r wordpress mysql
	rm .env

password:
	@pwgen -cns 255 1

env:
ifeq (,$(wildcard ./.env))
	touch .env
	$(shell echo "MYSQL_ROOT_PASSWORD=$(shell ${MAKE} password)" >> .env)
	@$(eval MYSQL_PASSWORD := $(shell ${MAKE} password))
	$(shell echo "MYSQL_PASSWORD=$(MYSQL_PASSWORD)" >> .env)
	$(shell echo "WORDPRESS_DB_PASSWORD=$(MYSQL_PASSWORD)" >> .env)
endif

# Docker
docker-up-dev: env
	$(shell export $(xargs < /var/www/services/h-software.de/httpdocs/.env) && echo $(MYSQL_PASSWORD))
	#docker-compose up

docker-down:
	docker-compose stop

# Database
import-db:
	
