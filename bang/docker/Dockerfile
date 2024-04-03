FROM ubuntu:24.04
RUN apt update -y

# sudo
RUN apt install -y sudo && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN apt install -y \
    git \
    python-is-python3 \
    python3-pip \
    python3-venv \
    wget

# Bazel.
RUN wget -O /usr/bin/bazelisk https://github.com/bazelbuild/bazelisk/releases/download/v1.19.0/bazelisk-linux-amd64 && \
    chmod a+x /usr/bin/bazelisk && \
    ln -s /usr/bin/bazelisk /usr/bin/bazel

# TODO(xiaoxq): Revisit this after ubuntu 24.04 is released.
RUN deluser ubuntu
