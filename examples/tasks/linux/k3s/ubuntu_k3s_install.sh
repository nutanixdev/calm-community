#!/bin/bash

set -e

if [ @@{K3S_INSTALL}@@ != True ] ; then
    exit 0
fi

echo "Creating resolv.conf.k3s..."
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf.k3s

echo "Installing K3s..."
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644 --resolv-conf /etc/resolv.conf.k3s

echo "Waiting for K3s to start..."
until kubectl get nodes | grep -i "Ready"; do sleep 2; done

echo "K3s installed..."
kubectl get nodes -o wide
kubectl config view --raw > ~/.kube/config
chmod 600 ~/.kube/config

echo "K3s patching Traefik with hostNetwork: true ..."
until kubectl -n kube-system get deployment traefik | grep -i "1/1"; do sleep 2; done
kubectl -n kube-system patch deployment traefik --patch '{"spec":{"template":{"spec":{"hostNetwork":true}}}}'

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