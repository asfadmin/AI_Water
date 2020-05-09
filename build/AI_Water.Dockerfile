FROM osgeo/gdal:ubuntu-full-latest

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-missing --no-install-recommends \
    python3.7 \
    python3-pip \
    make \
    nano

RUN pip3 install \
    keras \
    tensorflow \
    pyperclip \
    matplotlib \
    pytest \
    hypothesis \
    pytest-cov \
    mock \
    typing-extensions \
    asf_hyp3






