#!/bin/bash

set -e

echo "Uninstalling any old version..."
sudo yum remove -y \
    docker \
    docker-client \
    docker-client-latest \
    docker-common \
    docker-latest \
    docker-latest-logrotate \
    docker-logrotate \
    docker-engine

echo "Setting up Docker repository..."
sudo yum install -y yum-utils
sudo yum-config-manager \
   --add-repo \
   https://download.docker.com/linux/centos/docker-ce.repo

echo "Installing Docker CE..."
sudo yum install -y docker-ce docker-ce-cli containerd.io

echo "Starting Docker service..."
sudo systemctl start docker

echo "Enabling Docker service..."
sudo systemctl enable docker

echo "Adding $(whoami) to Docker group... "
sudo usermod -aG docker $(whoami)