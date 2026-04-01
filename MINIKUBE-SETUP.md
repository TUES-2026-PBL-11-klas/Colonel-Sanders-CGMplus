# Minikube Dev/Test Cluster + Cloudflare Guide

This guide configures the hosted test machine to behave close to production:

- Kubernetes on minikube
- ingress-nginx
- Argo CD GitOps sync
- Vault + External Secrets for injected runtime secrets
- images from GHCR
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

Argo CD will sync ingress + gtfs + auth + vault external secrets from `development` branch.

## 5) Configure Vault Secrets for Dev/Test

ExternalSecret keys expected:

- `secret/data/gtfs`:
	- `POSTGRES_USER`
	- `POSTGRES_PASSWORD`
	- `POSTGRES_DB`
	- `POSTGRES_PORT`
- `secret/data/auth`:
	- `SQLALCHEMY_DATABASE_URI`
	- `JWT_SECRET`

## 6) Configure Cloudflare Tunnel

```bash
cloudflared tunnel create cgmplus-dev
cloudflared tunnel route dns cgmplus-dev cgmplus-dev.example.com
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80
cloudflared tunnel run cgmplus-dev --url http://localhost:8080
```

Keep host in [gitops/ingress/ingress.yaml](gitops/ingress/ingress.yaml) aligned with your Cloudflare DNS.

## 7) Deployment Flow

1. Push to `development`.
2. Service build workflow builds/pushes images to GHCR.
3. Workflow updates image tags in GitOps manifests on `development`.
4. Argo CD syncs and rolls out new pods in minikube.

## 8) Azure Production Notes

Terraform + Helm are valid for production too.

Typical production changes:

1. point Terraform providers to AKS kubeconfig
2. apply [gitops/environments/prod/CGMplus-prod.yaml](gitops/environments/prod/CGMplus-prod.yaml)
3. replace dev Vault flow with Azure-managed secrets (for example Key Vault + External Secrets provider)
4. optionally move image registry from GHCR to ACR

## Cleanup

```bash
minikube delete -p cgmplus-dev
```
