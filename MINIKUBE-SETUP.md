# Minikube Dev/Test Cluster + Cloudflare Guide

This guide configures the hosted test machine to behave close to production:

- Kubernetes on minikube
- ingress-nginx
- Argo CD GitOps sync
- Vault + External Secrets for injected runtime secrets
- images from Docker Hub
- Cloudflare Tunnel exposure

## Branch to Environment Mapping

- `development` -> test cluster (minikube + Cloudflare)
- `main` -> production (Azure target)

Argo CD dev app tracks `development` branch in:
[gitops/environments/dev/CGMplus-dev.yaml](gitops/environments/dev/CGMplus-dev.yaml)

Prod Argo CD app manifest is:
[gitops/environments/prod/CGMplus-prod.yaml](gitops/environments/prod/CGMplus-prod.yaml)

## 1) Prerequisites on the Hosted Test PC

1. Docker Desktop
2. minikube
3. kubectl
4. Helm
5. Terraform
6. cloudflared

## 2) Create the minikube Cluster

Windows:

```powershell
.\minikube-cluster-setup.ps1
```

Linux/macOS:

```bash
chmod +x minikube-cluster-setup.sh
./minikube-cluster-setup.sh
```

The scripts create/update minikube profile `cgmplus-dev`.

## 3) Install Cluster Addons with Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
kubeconfig_path     = "~/.kube/config"
discord_webhook_url = "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"

enable_argocd           = true
enable_vault            = true
enable_external_secrets = true
enable_observability    = true
```

Apply:

```bash
terraform init
terraform plan
terraform apply
```

## 4) Apply Argo CD Dev Application

```bash
kubectl apply -f ../gitops/environments/dev/CGMplus-dev.yaml -n argocd
kubectl get application -n argocd
```

Argo CD will sync ingress + postgres + gtfs + auth + vault external secrets from `development` branch.

## 5) Configure Vault Secrets for Dev/Test

ExternalSecret keys expected:

- `secret/data/auth`:
	- `POSTGRES_HOST` (use `auth-postgres`)
	- `POSTGRES_PORT` (usually `5432`)
	- `POSTGRES_DB`
	- `POSTGRES_USER`
	- `POSTGRES_PASSWORD`
	- `JWT_SECRET`

The auth service builds `SQLALCHEMY_DATABASE_URI` from those fields at runtime.

PostgreSQL runs in-cluster as service `auth-postgres` in namespace `services`.

## 6) Configure Cloudflare Tunnel(FREE)

```bash
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80
cloudflared tunnel --url http://localhost:8080
```

Keep host in [gitops/ingress/ingress.yaml](gitops/ingress/ingress.yaml) aligned with your Cloudflare DNS.

### Exposure Policy (Recommended)

Expose only the app ingress externally. Keep Argo CD, Grafana, Prometheus, Loki, Alertmanager, and Vault internal (ClusterIP) and access them only with local port-forward.

External exposure (only ingress controller):

```bash
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80
cloudflared tunnel run cgmplus-dev --url http://localhost:8080
```

Localhost-only admin/observability access:

```bash
# Argo CD UI
kubectl port-forward -n argocd svc/argocd-server 8081:443
# Open https://localhost:8081

# Grafana
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80
# Open http://localhost:3000

# Prometheus
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090
# Open http://localhost:9090

# Alertmanager
kubectl port-forward -n monitoring svc/kube-prometheus-stack-alertmanager 9093:9093
# Open http://localhost:9093

# Loki API
kubectl port-forward -n monitoring svc/loki 3100:3100
# Open http://localhost:3100/ready

# Vault UI
kubectl port-forward -n vault svc/vault-ui 8200:8200
# Open http://localhost:8200
```

Quick verification that only app ingress is exposed:

```bash
kubectl get ingress -A
kubectl get svc -A
```

You should see only your application ingress resource in namespace `services`, while Argo CD and monitoring services remain `ClusterIP`.

## 7) Deployment Flow

1. Push to `development`.
2. Service build workflow builds/pushes images to Docker Hub.
3. Workflow updates image tags in GitOps manifests on `development`.
4. Argo CD syncs and rolls out new pods in minikube.

## 8) Azure Production Notes

Terraform + Helm are valid for production too.

Typical production changes:

1. point Terraform providers to AKS kubeconfig
2. apply [gitops/environments/prod/CGMplus-prod.yaml](gitops/environments/prod/CGMplus-prod.yaml)
3. replace dev Vault flow with Azure-managed secrets (for example Key Vault + External Secrets provider)
4. optionally move image registry from Docker Hub to ACR

## Cleanup

```bash
minikube delete -p cgmplus-dev
```
