FROM osgeo/gdal:ubuntu-full-latest

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-missing --no-install-recommends \
    python3.8 \
    python3-pip \
    python3-tk \
    make \
    git \
    xauth

RUN pip3 install \
    keras \
    tensorflow \
    pyperclip \
    matplotlib \
    pytest \
    hypothesis \
    pytest-cov \
    pytest-datadir \
    pytest-mock \
    mock \
    typing-extensions \
    asf_hyp3
