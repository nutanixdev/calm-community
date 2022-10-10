#!/bin/bash

set -e

echo "Uninstalling any old version..."
sudo apt-get remove -y \
    docker \
    docker-engine \
    docker.io \
    containerd \
    runc  

echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

echo "Setting up Docker repository..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Installing Docker Engine..."
sudo apt-get update -y
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