
.ONESHELL:

.PHONY: container

image: build/AI_Water.Dockerfile
	cd build && \
	xhost + && \
	docker build -f AI_Water.Dockerfile -t ai-water .

container: image
	docker run -it --rm \
		-v ${PWD}:/AI_Water \
		-v ~/.aws:/root/.aws \
		-v ~/Downloads:/root/Downloads \
		--name=AI_Water-dev \
		--workdir="/AI_Water" \
		--net=host \
		-e DISPLAY \
		-v ${HOME}/.Xauthority:/home/user/.Xauthority \
		ai-water:latest

test:
	pytest --cov-report term-missing --cov=src