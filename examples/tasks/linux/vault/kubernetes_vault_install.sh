#!/bin/bash

set -e

if [ @@{VAULT_INSTALL}@@ != True ] ; then
    exit 0
fi

printf "\n=======> Installing Vault CLI locally...\n"
if command -v apt &> /dev/null
then
    sudo apt install -y gpg
    wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg >/dev/null
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
    sudo apt update && sudo apt install -y vault
fi


printf "\n=======> Adding Hashicorp Helm repository...\n"
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
    - host: localhost

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
printf "\n=======> Vault successfully installed!"

kubectl exec -ti vault-0 -- vault operator init -key-shares=1 -key-threshold=1 -format=json > ~/.keys
chmod 600 ~/.keys

echo "alias vault='env VAULT_ADDR=http://localhost/ vault'" >> ~/.bashrc

printf "\n=======> Connection details...\n"
echo "Login URL: https://${VAULT_HOST}"
echo "Vault keys available via SSH in: ~/.keys"

if [ @@{VAULT_PRINT_KEYS}@@ == True ] ; then
    export VAULT_UNSEAL=$(jq -r '.unseal_keys_b64[0]' ~/.keys)
    export VAULT_TOKEN=$(jq -r '.root_token' ~/.keys)
    echo "Vault unseal key: ${VAULT_UNSEAL}"
    echo "Vault root token: ${VAULT_TOKEN}"
fi

printf "\n=======> Setting Service variables\n"
if [ @@{VAULT_PRINT_KEYS}@@ == True ] ; then
    echo "VAULT_UNSEAL = ${VAULT_UNSEAL}"
    echo "VAULT_TOKEN = ${VAULT_TOKEN}"
fi

echo "VAULT_HOST = ${VAULT_HOST}"
