USER_DISPLAY := {$DISPLAY}

.ONESHELL:

.PHONY: container set-mac-display

image: build/AI_Water.Dockerfile
	cd build && \
	xhost + && \
	docker build -f AI_Water.Dockerfile -t ai-water .

container-mac: image
	docker run -it --rm \
		-v ${PWD}:/AI_Water \
		-v ~/.aws:/root/.aws \
		-v ~/Downloads:/root/Downloads \
		--name=AI_Water-test \
		--workdir="/AI_Water" \
		--net=host \
		-e DISPLAY=host.docker.internal:0 \
		-v ~/Xauthority:/home/user/.Xauthority \
		ai-water:latest \
		bash -c "pip3 install -e . ; bash"

container: image
	docker run -it --rm \
		-v ${PWD}:/AI_Water \
		-v ~/.aws:/root/.aws \
		-v ~/Downloads:/root/Downloads \
		--name=AI_Water-test \
		--workdir="/AI_Water" \
		--net=host \
		-e ${DISPLAY}:${DISPLAY} \
		-v ~/Xauthority:/home/user/.Xauthority \
		ai-water:latest \
		bash -c "pip3 install -e . ; bash"

test:
	pytest --cov-report term-missing --cov=src

test-gui:
	apt-get install x11-apps -y; xeyes