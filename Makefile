hello:
	echo "Hello world"

run_app:
	./hdtgm_server/bin/python ./app.py 

build-app:
	docker build --tag hdtgm-player .

run-app:
	docker run -d -p 80:5000 --name hdtgm-player hdtgm-player 