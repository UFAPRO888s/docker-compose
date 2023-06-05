# FROM ubuntu:18.04
# FROM balenalib/raspberrypi3-python:3.9-bullseye
# FROM balenalib/raspberrypi3-python:3.9-bullseye-build
# FROM balenalib/orange-pi-lite-debian-node:latest
FROM balenalib/orange-pi-lite-python:3.9-bullseye
# FROM balenalib/orange-pi-lite-python:3.9
#Enforces cross-compilation through Quemu
RUN [ "cross-build-start" ]

RUN apt-get update -y && apt-get install -y apt-utils
RUN apt-get install -y locales locales-all
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
RUN apt-get update -y
RUN apt-get install -y \
        alsa* \
        apt-utils \
        autoconf \
        automake \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        ffmpeg \
        g++ \
        gdb \
        git \
        gstreamer1.0-plugins-* \
        libass-dev \
        libatlas-base-dev \
        libavcodec-dev \
        libavformat-dev \
        libcaca-dev \
        libcurl4-openssl-dev \
        libgstreamer-plugins-base1.0-dev \
        libgstreamer1.0-dev \
        libgtk-3-dev \
        libjpeg-dev \
        libmp3lame-dev \
        libopencore-amrnb-dev \
        libopencore-amrwb-dev \
        libopenexr-dev \
        libopus-dev \
        libpcre3 \
        libpcre3-dev \
        libpng-dev \
        libprotobuf-dev \
        librtmp-dev \
        libsm6 \
        libsndfile1-dev \
        libssl-dev \
        libswscale-dev \
        libtheora-dev \
        libtiff-dev \
        libtool \
        libvncserver-dev \
        libvo-aacenc-dev \
        libvo-amrwbenc-dev \
        libvorbis-dev \
        libvpx-dev \
        libwebp-dev \
        libx265-dev \
        libxext6 \
        libxml2 \
        libxml2-dev \
        libxrender-dev \
        libxslt-dev \
        nginx \
        openssl \
        openssh-server \
        pkg-config \
        protobuf-compiler \
        python-is-python3 \
        python3 \
        python3-dev \
        python3-numpy \
        python3-opencv \
        python3-pil \
        python3-pip \
        python3-setuptools \
        python3-scipy \
        python3-sklearn \
        python3-sklearn-lib \
        python3-plotly \
        python3-pandas \
        python3-matplotlib \ 
        sudo \
        swig \
        tar \
        unzip \
        valgrind \
        vim \
        wget  \
        x264 \
        x265 \
        zlib1g-dev 
WORKDIR /tmp
COPY ./dependency/ /tmp

ARG NUM_JOBS=12
# # Build the latest cmake
# ARG CMAKE_VERSION=3.23.4
# RUN cd /tmp && \
#     wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz -O cmake-${CMAKE_VERSION}.tar.gz --progress=bar:force && \
#     tar zxf cmake-${CMAKE_VERSION}.tar.gz && \
#     rm cmake-${CMAKE_VERSION}.tar.gz && \
#     cd ./cmake-${CMAKE_VERSION} && \
#     ./configure --system-curl && \
#     make -j${NUM_JOBS} && \
#     make install && \
#     rm -rf /tmp/*

# Build and install opencv
# ARG OPENCV_VERSION=4.6.0
# RUN cd /tmp && \
#     wget https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip -O opencv.zip --progress=bar:force && \
#     wget https://github.com/opencv/opencv_contrib/archive/${OPENCV_VERSION}.zip -O opencv_contrib.zip --progress=bar:force && \
#     unzip opencv.zip && \
#     unzip opencv_contrib.zip && \
#     mkdir -p build && cd build && \
#     cmake -DOPENCV_EXTRA_MODULES_PATH=../opencv_contrib-${OPENCV_VERSION}/modules ../opencv-${OPENCV_VERSION} && \
#     cmake --build . -j${NUM_JOBS} && \
#     make install && \
#     rm -rf /tmp/*
# RUN pip3 install opencv-contrib-python

# RUN apt install -y python3-opencv


# ARG ZLIB_VERSION=1.2.0.4
# RUN cd /tmp && \
#     wget http://www.zlib.net/fossils/zlib-${ZLIB_VERSION}.tar.gz && \
#     tar -xvzf zlib-${ZLIB_VERSION}.tar.gz && \
#     cd zlib-${ZLIB_VERSION} && \
#     ./configure --prefix=/usr/local/zlib && \
#     make install && \
#     rm -rf /tmp/*
RUN apt-get install -y ./zlib_1.2.0.4-1_armhf.deb

# RUN wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py --progress=bar:force
# RUN python3 get-pip.py --force-reinstall
# RUN pip3 -V

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install Cython imutils

# RUN pip3 install spidev
# RUN pip3 install protobuf

RUN pip3 install -r requirements.txt
# RUN pip3 install scipy
# RUN pip3 install scikit-learn
# RUN pip3 install --upgrade opencv-python
RUN pip3 install onnx-1.12.0-cp39-cp39-linux_armv7l.whl
RUN pip3 install onnxruntime-1.8.1-cp39-cp39-linux_armv7l.whl

# COPY ./requirements.txt /tmp/requirements.txt 
# RUN pip3 install --upgrade pip
# RUN pip3 install OrangePi.GPIO
RUN pip3 install OPi.GPIO
# RUN apt-get update && apt-get -y install openssh-server
# COPY vsftpd.conf /etc/vsftpd.conf

RUN apt-get update && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# RUN service vsftpd restart
COPY nginx/* /etc/nginx/
COPY app /app
RUN ln -sf /app/html /var/www/html
RUN mkdir -p /streaming
RUN mount -t tmpfs -o size=128m tmpfs /var/www/html/streaming

WORKDIR /app


RUN [ "cross-build-end" ]

EXPOSE 22 80 4000
CMD [ "run.sh" ]
ENTRYPOINT ["bash"]


