#!/bin/bash

set -e

if [ @@{AWX_INSTALL}@@ != True ] ; then
    exit 0
fi

echo "Installing dependencies..."
sudo apt install -y make

echo "Cloning repository..."
cd ~
git clone https://github.com/ansible/awx-operator.git
cd awx-operator

echo "Changing to latest version branch..."
AWX_OPERATOR_LATEST_VER=$(curl -LsI -o /dev/null -w %{url_effective} https://github.com/ansible/awx-operator/releases/latest | rev | cut -d'/' -f1 | rev)
git checkout $AWX_OPERATOR_LATEST_VER

echo "Installing AWX Operator..."
export NAMESPACE=awx
make deploy

