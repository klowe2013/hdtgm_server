hello:
	echo "Hello world"

local-run:
	gunicorn --bind 0.0.0.0:80 main:app

build-app:
	echo "Cleaning up old container" \
	&& docker stop hdtgm-player && docker rm hdtgm-player \
	&& echo "Building HDTGM player (prod)" \
	&& docker build --tag hdtgm-player . \
	&& echo "Creating container..." \
	&& docker run -d -p 80:5000 --name hdtgm-player hdtgm-player 

run-app:
	docker start hdtgm-player 	

build-dev:
	echo "Building HDTGM player (dev)" \
	&& docker build --tag hdtgm-dev . \
	&& echo "Creating container..." \
	&& docker run -d -v "${CURDIR}/mounted_data/":/hdtgm-player/ -p 5000:5000 --name hdtgm-dev hdtgm-dev 

run-dev:
	docker run -d -v "$(CURDIR)/mounted_data/":/hdtgm-player/ -p 5000:5000 --name hdtgm-dev hdtgm-dev 

debug-dev:
	./hdtgm_server/bin/python ./main.py
