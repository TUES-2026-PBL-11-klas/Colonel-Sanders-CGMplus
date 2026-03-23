# Kind Cluster Setup & Terraform Apply Guide

## Prerequisites

Install these tools (if not already installed):

1. **Docker Desktop** - https://www.docker.com/products/docker-desktop
2. **kind** - `choco install kind` or `brew install kind`
3. **kubectl** - `choco install kubernetes-cli` or `brew install kubectl`
4. **Helm** - `choco install helm` or `brew install helm`
5. **Terraform** - `choco install terraform` or `brew install terraform`

## Step 1: Create kind Cluster

### On Windows PowerShell:
```powershell
.\kind-cluster-setup.ps1
```

### On macOS/Linux (bash):
```bash
chmod +x kind-cluster-setup.sh
./kind-cluster-setup.sh
```

This creates a single-node Kubernetes cluster suitable for dev/test.

## Step 2: Verify Cluster Access

```bash
kubectl get nodes
kubectl get pods -n kube-system
```

The kubeconfig is automatically saved to `~/.kube/config`.

## Step 3: Bootstrap Platform with Terraform

```bash
cd terraform

# Copy and customize tfvars
cp terraform.tfvars.example terraform.tfvars

# Edit with your Discord webhook URL
# On Windows: code terraform.tfvars
# On macOS: open -e terraform.tfvars
```

Edit `terraform.tfvars` and set:
```hcl
kubeconfig_path     = "~/.kube/config"
discord_webhook_url = "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"

enable_argocd           = true
enable_vault            = true
enable_external_secrets = true
enable_observability    = true
```

Then apply:

```bash
terraform init
terraform plan
terraform apply
```

**Expected output:**
- Creates 6 namespaces: `argocd`, `external-secrets`, `gtfs`, `ingress-nginx`, `monitoring`, `vault`
- Installs Helm releases for each addon
- Takes 3-5 minutes first time (pulling images)

**Troubleshooting:**
- If helm release timeouts: increase `timeout` in `main.tf` (already set to 600 seconds)
- If Loki fails: check storage is enabled and stateful sets can mount volumes
- If external-secrets fails: check CRDs installed by running `kubectl get crd | grep external`

## Step 4: Verify Installations

```bash
# Check namespaces
kubectl get ns

# Check pods in each namespace
kubectl get pods -n ingress-nginx
kubectl get pods -n monitoring
kubectl get pods -n vault
kubectl get pods -n external-secrets
kubectl get pods -n argocd

# Check helm releases
helm list -A
```

## Step 5: Access Services

### Prometheus
```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090 &
# Open: http://localhost:9090
```

### Grafana
```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:3000 &
# Open: http://localhost:3000
# Credentials: admin / admin
```

### Vault
```bash
kubectl port-forward -n vault svc/vault 8200:8200 &
# Open: http://localhost:8200
# Token (dev mode): root
```

### Argo CD
```bash
kubectl port-forward -n argocd svc/argo-cd-argocd-server 8080:443 &
# Open: https://localhost:8080
# Initial password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

## Step 6: Deploy GTFS Application

```bash
# Apply Argo CD Application
kubectl apply -f ../gitops/environments/dev/gtfs-application.yaml -n argocd

# Monitor sync
kubectl get application -n argocd
kubectl get pods -n gtfs
```

## Step 7: Configure Cloudflare Tunnel (Optional for Team Access)

Install Cloudflare Tunnel and route DNS hostname to `localhost:80`:

```bash
cloudflared tunnel create gtfs-dev
cloudflared tunnel route dns gtfs-dev gtfs-dev.example.com
cloudflared tunnel run gtfs-dev --url http://localhost:80
```

Update `gitops/ingress/ingress.yaml` host to match and re-apply.

## Cleanup: Delete Cluster

```bash
kind delete cluster --name=gtfs-dev
```

This removes the entire cluster but keeps kubeconfig entry (safe to delete manually).
