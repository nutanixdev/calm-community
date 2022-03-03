#!/bin/bash

set -e

if [ @@{K3S_INSTALL}@@ != True ] ; then
    exit 0
fi

echo "Installing K3s..."
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644

echo "Waiting for K3s to start..."
until kubectl get nodes | grep -i "Ready"; do sleep 2 ; done

echo "K3s installed..."
kubectl get nodes -o wide