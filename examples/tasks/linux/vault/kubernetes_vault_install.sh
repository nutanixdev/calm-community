#!/bin/bash

set -e

if [ @@{VAULT_INSTALL}@@ != True ] ; then
    exit 0
fi

echo "Installing dependencies..."
helm repo add hashicorp https://helm.releases.hashicorp.com

echo "Launching Vault installation..."
export VAULT_HOST="@@{address}@@.nip.io"
helm install vault hashicorp/vault \
    --set "server.ingress.enabled=true" \
    --set "server.ingress.hosts[0].host=${VAULT_HOST}"

echo "Waiting for Vault to install..."
timeout 10m bash -c '
sleep 60
response=$(curl --write-out "%{http_code}" --silent --output /dev/null ${VAULT_HOST})
while [ $response -ne 307 ]
do
  response=$(curl --write-out "%{http_code}" --silent --output /dev/null ${VAULT_HOST})
  echo Response: Installing...
  response=$response 
  sleep 20
done'

mkdir -p ~/.vault
kubectl exec -ti vault-0 -- vault operator init -key-shares=1 -key-threshold=1 -format=json > ~/.vault/keys
chmod 600 ~/.vault/keys

echo "Vault successfully installed! Login URL: https://${VAULT_HOST}"
echo "Vault keys available in ~/.vault/keys"
echo "VAULT_HOST = ${VAULT_HOST}"

if [ @@{VAULT_PRINT_KEYS}@@ == True ] ; then
    VAULT_UNSEAL_KEY=$(jq -r '.unseal_keys_b64[0]' ~/.vault/keys)
    VAULT_ROOT_TOKEN=$(jq -r '.root_token' ~/.vault/keys)
    echo "VAULT_UNSEAL_KEY = ${VAULT_UNSEAL_KEY}"
    echo "VAULT_ROOT_TOKEN = ${VAULT_ROOT_TOKEN}"
fi