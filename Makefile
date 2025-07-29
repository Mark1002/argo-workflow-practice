.PHONY: build create-server

build-docker:
	docker build -t argo-workflow-practice:v0.1.0 .

create-server:
	./scripts/create-server.sh
