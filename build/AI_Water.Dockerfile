FROM ubuntu

RUN apt-get update -y && \
    apt-get install -y make nano git gcc && \
    apt-get install libgdal-dev --no-install-recommends -y
