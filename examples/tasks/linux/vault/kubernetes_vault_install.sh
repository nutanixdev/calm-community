#!/bin/bash

set -e

if [ @@{VAULT_INSTALL}@@ != True ] ; then
    exit 0
fi

echo "Installing dependencies..."
helm repo add hashicorp https://helm.releases.hashicorp.com

echo "Launching Vault installation..."
export VAULT_HOST="@@{address}@@.nip.io"

# https://www.vaultproject.io/docs/platform/k8s/helm/configuration

cat <<EOF >>values_patch.yaml
server:
  ingress:
    enabled: true
    hosts:
    - host: ${VAULT_HOST}

  standalone:
    config: |
      ui = true

      listener "tcp" {
        tls_disable = 1
        address = "[::]:8200"
        cluster_address = "[::]:8201"
        x_forwarded_for_authorized_addrs = "0.0.0.0/0"
      }

      storage "file" {
        path = "/vault/data"
      }
EOF
helm install vault hashicorp/vault --values values_patch.yaml

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