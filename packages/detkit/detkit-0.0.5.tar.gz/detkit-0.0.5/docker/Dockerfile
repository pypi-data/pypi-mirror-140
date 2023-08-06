# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE

# -----------------------------------------------------------------------------
# How to build
#   $ cd ..  # go to root dir of package
#   $ docker build . -t sameli/detkit -f docker/Dockerfile
#
# How to run:
#   $ docker run -it -v/host_dir:/image_dir detkit
# -----------------------------------------------------------------------------

# -----
# Build
# -----

FROM ubuntu:20.04 as builder
MAINTAINER Siavash Ameli <samei@berkeley.edu>
LABEL Description="detkit python package"

# Install python3
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-dev \
        python3-pip \
        build-essential \
        libgomp1 \
        wget \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Build package wheel
# ENV USE_CUDA=1
RUN mkdir /tmp/detkit
ADD . /tmp/detkit/
WORKDIR /tmp/detkit
RUN rm -rf build dist
RUN /usr/bin/python3 setup.py bdist_wheel

# -------
# Runtime
# -------

FROM ubuntu:20.04

# Install python3 and libcudablas, libcusparse, since they are not in the NVIDIA
# cuda's "base" image.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
        python3-pip \
        libgomp1 \
        vim \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the wheel from the previous build (on NVIDIA cuda-devel image) and
# install it on this image.
COPY --from=builder /tmp/detkit/dist/*.whl /tmp/
RUN /usr/bin/python3 -m pip --no-cache-dir install /tmp/*.whl
RUN rm /tmp/*.whl

# Create a startup file to auto-import package when python starts
RUN echo "import detkit" > /home/.start_python.py
ENV PYTHONSTARTUP=/home/.start_python.py
ENV PATH=$PATH:/usr/bin/
RUN /usr/bin/python3 -m pip install --upgrade pip ipython jupyter

# Change working directory for entrypoint
VOLUME ["/root"]
WORKDIR /root

# ENTRYPOINT ["/bin/bash"]
CMD ["/usr/bin/python3"]
