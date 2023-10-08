hello:
	echo "Hello world"

test-run:
	./hdtgm_server/bin/python ./app.py

build-app:
	docker build --tag hdtgm-player .

run-app:
	docker run -d -v "$(PWD)/mounted_data/":/hdtgm-player/data/ -p 80:5000 --name hdtgm-player hdtgm-player 

compose-kafka:
	docker-compose --file ./dockerfiles/docker-compose-kafka.yml up -d

compose-cassandra:
	docker-compose --file ./dockerfiles/docker-compose-cassandra.yml up -d

kafka-down:
	docker-compose --file ./dockerfiles/docker-compose-kafka.yml down

cassandra-down:
	docker-compose --file ./dockerfiles/docker-compose-cassandra.yml down

deploy-gcp:
	gcloud app deploy 
