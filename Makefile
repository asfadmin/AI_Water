
.ONESHELL:

.PHONY: container

image: build/AI_Water.Dockerfile
	cd build && \
	docker build -f AI_Water.Dockerfile -t aiwater .


container: image
	docker run -it --rm \
		-v ${PWD}:/AI_Water \
		-v ~/.aws:/root/.aws \
		--name=AI_Water-dev \
		--workdir="/AI_Water" \
		aiwater:latest


