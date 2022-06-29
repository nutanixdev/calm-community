#!/bin/bash

set -e

printf "\n=======> Installing Helm PGP key..."
curl -s https://baltocdn.com/helm/signing.asc | sudo apt-key add -
sudo apt-get -qq install -y apt-transport-https

printf "\n=======> Adding Helm repo..."
printf "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list

printf "\n=======> Updating packages..."
sudo apt-get -qq update -y

printf "\n=======> Installing Helm and JQ packages..."
sudo apt-get -qq install -y helm jq