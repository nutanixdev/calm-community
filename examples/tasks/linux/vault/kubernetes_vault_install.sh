#!/bin/bash

set -e

if [ @@{VAULT_INSTALL}@@ != True ] ; then
    exit 0
fi

printf "\n=======> Adding Hashicorp's Helm repository...\n"
helm repo add hashicorp https://helm.releases.hashicorp.com

printf "\n=======> Preparing Vault installation...\n"
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

printf "\n=======> Launching Vault installation...\n"
helm install vault hashicorp/vault --values values_patch.yaml

printf "\n=======> Waiting for Vault to install...\n"
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

echo "alias vault='kubectl exec vault-0 -- env VAULT_TOKEN=$(jq -r .root_token ~/.vault/keys) vault'" >> ~/.bashrc

printf "\n=======> Connection details...\n"
echo "Vault successfully installed!\nLogin URL: https://${VAULT_HOST}"
echo "Vault keys available via SSH in: ~/.vault/keys"

if [ @@{VAULT_PRINT_KEYS}@@ == True ] ; then
    VAULT_UNSEAL_KEY=$(jq -r '.unseal_keys_b64[0]' ~/.vault/keys)
    VAULT_ROOT_TOKEN=$(jq -r '.root_token' ~/.vault/keys)
    echo "Vault unseal key: ${VAULT_UNSEAL_KEY}"
    echo "Vault root token: ${VAULT_ROOT_TOKEN}"
fi

printf "\n=======> Setting Service variables\n"
if [ @@{VAULT_PRINT_KEYS}@@ == True ] ; then
    echo "VAULT_UNSEAL_KEY = ${VAULT_UNSEAL_KEY}"
    echo "VAULT_ROOT_TOKEN = ${VAULT_ROOT_TOKEN}"
fi

echo "VAULT_HOST = ${VAULT_HOST}"
