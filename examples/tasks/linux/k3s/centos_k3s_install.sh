#!/bin/bash

set -e

if [ @@{K3S_INSTALL}@@ != True ] ; then
    exit 0
fi

echo "Disabling Firewalld..."
sudo systemctl disable firewalld --now

echo "Installing dependencies..."
sudo dnf install -y \
    git \
    make

echo "Installing K3s..."
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644

echo "Waiting for K3s to start..."
until kubectl get nodes | grep -i "Ready"; do sleep 2 ; done

echo "K3s installed..."
kubectl get nodes -o wide
kubectl config view --raw > ~/.kube/config
chmod 600 ~/.kube/config

DOCKER_HUB_USERNAME="@@{DOCKER_HUB_USERNAME}@@"
DOCKER_HUB_PASSWORD="@@{DOCKER_HUB_PASSWORD}@@"

if [ -z "$DOCKER_HUB_USERNAME" ] && [ -z "$DOCKER_HUB_PASSWORD" ] ; then
    exit 0
else
    echo "Setting Docker Hub credentials to avoid pull rate limits..."
    kubectl create secret docker-registry docker-hub-secret \
        --docker-username=${DOCKER_HUB_USERNAME} \
        --docker-password=${DOCKER_HUB_PASSWORD}

    kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "docker-hub-secret"}]}' 
fi