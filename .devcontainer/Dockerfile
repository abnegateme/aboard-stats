FROM python:3.15-slim-trixie

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    bash \
    build-essential \
    ca-certificates \
    curl \
    git \
    less \
    openssh-client \
    sudo \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd vscode \
    && useradd \
    --gid vscode \
    --create-home \
    --shell /bin/bash \
    vscode \
    && echo "vscode ALL=(root) NOPASSWD:ALL" \
    > /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode

COPY requirements.txt /tmp/requirements.txt
COPY .devcontainer/requirements-dev.txt /tmp/requirements-dev.txt

RUN python3 -m pip install \
    --break-system-packages \
    --no-cache-dir \
    -r /tmp/requirements.txt \
    -r /tmp/requirements-dev.txt \
    && rm /tmp/requirements.txt /tmp/requirements-dev.txt

RUN mkdir -p /workspace /home/vscode/.codex \
    && chown -R vscode:vscode \
    /workspace \
    /home/vscode

USER vscode

WORKDIR /workspace
