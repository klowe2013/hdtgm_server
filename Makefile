hello:
	echo "Hello world"

tmp-test:
	echo "hello world" \
	&& echo "hello world line 2"

test-run:
	./hdtgm_server/bin/python ./main.py

build-app:
	echo "Cleaning up old container" \
	&& docker stop hdtgm-player && docker rm hdtgm-player \
	&& echo "Building HDTGM player (prod)" \
	&& docker build --tag hdtgm-player . \
	&& echo "Creating container..." \
	&& docker run -d -v "$(PWD)/mounted_data/":/hdtgm-player/data/ -p 80:5000 --name hdtgm-player hdtgm-player 

run-app:
	docker start hdtgm-player 	

build-dev:
	echo "Cleaning up old container" \
	&& docker stop hdtgm-dev && docker rm hdtgm-dev \
	&& echo "Building HDTGM player (dev)" \
	&& docker build --tag hdtgm-dev . \
	&& echo "Creating container..." \
	&& docker run -d -v "$(PWD)/mounted_data/":/hdtgm-player/data/ -p 5000:5000 --name hdtgm-dev hdtgm-dev 

run-dev:
	docker start hdtgm-dev 

	
