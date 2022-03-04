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
export NAMESPACE=@@{AWX_NAMESPACE}@@
make deploy

echo "Changing K3s context to awx namespace..."
sudo kubectl config set-context --current --namespace=$NAMESPACE

echo "Waiting for AWX Operator to start..."
until kubectl get pods -l control-plane=controller-manager | grep -P '^(?=.*2/2)(?=.*Running)' ; do sleep 2; done

echo "Creating AWX installer directory..."
cd ~
mkdir awx-installer
cd awx-installer

echo "Creating AWX SSL certificate..."
AWX_HOST="@@{address}@@.nip.io"
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -out ./tls.crt -keyout ./tls.key -subj "/CN=${AWX_HOST}/O=${AWX_HOST}" -addext "subjectAltName = DNS:${AWX_HOST}"

echo "Creating AWX installer files..."
cat <<EOF >>awx.yaml
---
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx
spec:
  # These parameters are designed for use with:
  # - AWX Operator: 0.17.0
  #   https://github.com/ansible/awx-operator/blob/0.17.0/README.md
  # - AWX: 20.0.0
  #   https://github.com/ansible/awx/blob/20.0.0/INSTALL.md

  admin_user: admin
  admin_password_secret: awx-admin-password

  ingress_type: ingress
  ingress_tls_secret: awx-secret-tls
  hostname: ${AWX_HOST}

  postgres_configuration_secret: awx-postgres-configuration

  postgres_storage_class: awx-postgres-volume
  postgres_storage_requirements:
    requests:
      storage: 8Gi

  projects_persistence: true
  projects_existing_claim: awx-projects-claim

  web_resource_requirements: {}
  task_resource_requirements: {}
  ee_resource_requirements: {}
EOF
cat <<EOF >>kustomization.yaml
---
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

generatorOptions:
  disableNameSuffixHash: true

secretGenerator:
  - name: awx-secret-tls
    type: kubernetes.io/tls
    files:
      - tls.crt
      - tls.key

  - name: awx-postgres-configuration
    type: Opaque
    literals:
      - host=awx-postgres
      - port=5432
      - database=awx
      - username=awx
      - password=@@{AWX_DB_PASSWORD}@@
      - type=managed

  - name: awx-admin-password
    type: Opaque
    literals:
      - password=@@{AWX_ADMIN_PASSWORD}@@

resources:
  - pv.yaml
  - pvc.yaml
  - awx.yaml
EOF
cat <<EOF >>pv.yaml
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: awx-postgres-volume
spec:
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  capacity:
    storage: 8Gi
  storageClassName: awx-postgres-volume
  hostPath:
    path: /data/postgres

---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: awx-projects-volume
spec:
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  capacity:
    storage: 2Gi
  storageClassName: awx-projects-volume
  hostPath:
    path: /data/projects
EOF
cat <<EOF >>pvc.yaml
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: awx-projects-claim
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 2Gi
  storageClassName: awx-projects-volume
EOF

echo "Creating directories for persistent data..."
sudo mkdir -p /data/postgres
sudo mkdir -p /data/projects
sudo chmod 755 /data/postgres
sudo chown 1000:0 /data/projects

echo "Deploying AWX..."
kubectl apply -k .

echo "Waiting for AWX to start..."
until [ $response -eq 200 ]; do response=$(curl --write-out '%{http_code}' --silent --output /dev/null ${AWX_HOST}); ((response=$response)); sleep 5; done

echo "Login URL: https://${AWX_HOST}"
echo "AWX_HOST = ${AWX_HOST}"