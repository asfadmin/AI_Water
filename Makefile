
.ONESHELL:

.PHONY: container-shell

image: build/AI_Water.Dockerfile
	cd build && \
	docker build -f AI_Water.Dockerfile -t aiwater .


container-shell: image
	docker run -it --rm \
		-v ${PROJECT_ROOTDIR}:/AI_Water \
		-v ~/.aws:/root/.aws \
		--name=AI_Water-dev \
		--workdir="/AI_Water" \
		aiwater:latest


