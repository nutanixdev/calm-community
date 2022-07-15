#!/bin/bash

set -e

if [ @@{K3S_INSTALL}@@ != True ] ; then
    exit 0
fi

printf "\n=======> Creating resolv.conf.k3s...\n"
echo "nameserver @@{K3S_DNS_SERVER}@@" | sudo tee /etc/resolv.conf.k3s

printf "\n=======> Installing K3s...\n"
curl -sfL https://get.k3s.io | sh -s - \
    --write-kubeconfig-mode 644 \
    --resolv-conf /etc/resolv.conf.k3s \
    --cluster-cidr @@{K3S_CLUSTER_CIDR}@@ \
    --service-cidr @@{K3S_SERVICE_CIDR}@@ \
    --cluster-dns @@{K3S_CLUSTER_DNS}@@

printf "\n=======> Waiting for K3s to start...\n"
until kubectl get nodes | grep -i "Ready"; do sleep 2; done

printf "\n=======> K3s installed...\n"
kubectl get nodes -o wide
kubectl config view --raw > ~/.kube/config
chmod 600 ~/.kube/config

printf "\n=======> K3s patching Traefik with hostNetwork: true ...\n"
until kubectl -n kube-system get deployment traefik | grep -i "1/1"; do sleep 2; done
kubectl -n kube-system patch deployment traefik --patch '{"spec":{"template":{"spec":{"hostNetwork":true}}}}'

DOCKER_HUB_USERNAME="@@{DOCKER_HUB_USERNAME}@@"
DOCKER_HUB_PASSWORD="@@{DOCKER_HUB_PASSWORD}@@"

if [ -z "$DOCKER_HUB_USERNAME" ] || [ -z "$DOCKER_HUB_PASSWORD" ] ; then
    exit 0
else
    printf "\n=======> Setting Docker Hub credentials to avoid pull rate limits...\n"
cat <<EOF | sudo tee /etc/rancher/k3s/registries.yaml
configs:
    registry-1.docker.io:
        auth:
            username: ${DOCKER_HUB_USERNAME}
            password: ${DOCKER_HUB_PASSWORD}
EOF

    sudo chmod 600 /etc/rancher/k3s/registries.yaml
    sudo systemctl restart k3s
fi