# Make sure to use real tabs for indentation, not spaces!
.PHONY: install test build run deploy clean logs

install:
	pip install -r requirements.txt

test:
	pytest tests/unit/

build:
	docker build -t gist-api:latest .

run:
	docker run -p 8080:8080 gist-api:latest

deploy:
	kubectl apply -f k8s/deployment.yaml
	kubectl apply -f k8s/service.yaml

clean:
	kubectl delete -f k8s/deployment.yaml
	kubectl delete -f k8s/service.yaml

logs:
	kubectl logs -l app=gist-api -f