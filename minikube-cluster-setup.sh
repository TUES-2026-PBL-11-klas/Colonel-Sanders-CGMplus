#!/bin/bash
# minikube-cluster-setup.sh
# Bootstrap a minikube Kubernetes cluster for CGMplus dev/test

set -e

CLUSTER_NAME="cgmplus-dev"

echo "[1] Checking prerequisites..."
if ! command -v minikube &> /dev/null; then
  echo "minikube not found. Install from https://minikube.sigs.k8s.io/docs/start/"
  exit 1
fi
if ! command -v kubectl &> /dev/null; then
  echo "kubectl not found. Install kubectl before continuing."
  exit 1
fi
if ! command -v helm &> /dev/null; then
  echo "Helm not found. Install from https://helm.sh/docs/intro/install/"
  exit 1
fi

echo "[2] Starting minikube profile '$CLUSTER_NAME' (this takes 2-5 minutes)..."
minikube start -p "$CLUSTER_NAME" --driver=docker --cpus=4 --memory=8192
minikube -p "$CLUSTER_NAME" update-context

echo "[3] Verifying cluster..."
kubectl cluster-info
kubectl get nodes

echo "[4] minikube cluster is ready for Terraform + Argo CD bootstrap"
echo ""
echo "Next steps:"
echo "  1. cd terraform"
echo "  2. cp terraform.tfvars.example terraform.tfvars"
echo "  3. Edit terraform.tfvars and keep enable_argocd/enable_vault/enable_external_secrets = true"
echo "  4. terraform init"
echo "  5. terraform apply"
echo "  6. kubectl apply -f ../gitops/environments/dev/CGMplus-dev.yaml -n argocd"
echo ""
echo "Cloudflare for test access:"
echo "  - Run: kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80"
echo "  - Then: cloudflared tunnel run cgmplus-dev --url http://localhost:8080"
