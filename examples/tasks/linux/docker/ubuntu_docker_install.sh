#!/bin/bash

set -e

echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

echo "Setting up Docker repository..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable"

echo "Installing Docker Engine..."
sudo apt-get update
sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-compose-plugin

echo "Starting Docker service..."
sudo systemctl start docker

echo "Enabling Docker service..."
sudo systemctl enable docker

echo "Adding $(whoami) to Docker group... "
sudo usermod -aG docker $(whoami)