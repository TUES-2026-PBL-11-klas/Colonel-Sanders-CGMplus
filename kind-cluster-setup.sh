#!/bin/bash
# kind-cluster-setup.sh
# Bootstrap a kind Kubernetes cluster for GTFS dev/test

set -e

CLUSTER_NAME="gtfs-dev"
KIND_CONFIG="kind-config.yaml"

echo "[1] Creating kind cluster configuration..."
cat > $KIND_CONFIG <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: $CLUSTER_NAME
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 80
        hostPort: 80
      - containerPort: 443
        hostPort: 443
EOF

echo "[2] Creating kind cluster (this takes 1-2 minutes)..."
kind create cluster --config=$KIND_CONFIG || {
  echo "Cluster already exists or error. Attempting to delete and recreate..."
  kind delete cluster --name=$CLUSTER_NAME || true
  kind create cluster --config=$KIND_CONFIG
}

echo "[3] Verifying cluster..."
kubectl cluster-info
kubectl get nodes

echo "[4] Installing Helm (if not present)..."
if ! command -v helm &> /dev/null; then
  echo "Helm not found. Install from https://helm.sh/docs/intro/install/"
  exit 1
fi

echo "[5] Ready for Terraform apply!"
echo ""
echo "Next steps:"
echo "  1. cd terraform"
echo "  2. cp terraform.tfvars.example terraform.tfvars"
echo "  3. Edit terraform.tfvars (set discord_webhook_url)"
echo "  4. terraform init"
echo "  5. terraform apply"
echo ""
echo "Cluster kubeconfig already configured in ~/.kube/config"
