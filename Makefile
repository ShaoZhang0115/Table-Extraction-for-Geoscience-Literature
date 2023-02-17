clean:
	@echo "--> Cleaning pyc files"
	find . -name "*.pyc" -delete

install: clean
	pip3 install -r requirements.txt

build:
	@echo "--> Building image"
	docker build --rm -t table-backend:latest .

dev:
	uvicorn backend.main:app --host 0.0.0.0 --port 8001 --log-config log.yaml --log-level debug --reload

up:
	docker-compose up -d

down:
	docker-compose down
