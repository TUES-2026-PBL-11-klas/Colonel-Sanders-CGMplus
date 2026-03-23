# Colonel-Sanders-CGMplus

GTFS microservice platform with local dev/test hosting, GitOps delivery, GHCR image registry, Vault-based secret management, Terraform IaC, and observability with Discord notifications.

## What was implemented

1. GitOps structure is now inside this repository under `gitops/`.
2. CI for GTFS now includes tests, secret scan, and Discord notifications.
3. CD now builds GTFS image, pushes to GHCR, updates `gitops/services/gtfs/deployment.yaml`, and commits back.
4. Terraform-based platform bootstrap was added under `terraform/`.
5. Vault + External Secrets manifests were added to provide cluster secrets to GTFS.
6. GTFS container image build file was added at `services/gtfs/Dockerfile`.

## Repository layout

```text
.github/workflows/
	gtfs.yaml            # CI: lint, test, smoke, secret scan, Discord
	deploy.yml           # CD: build/push GHCR + update in-repo GitOps
	infra.yaml           # Terraform validate pipeline + Discord

gitops/
	environments/dev/gtfs-application.yaml
	environments/prod/.gitkeep
	ingress/ingress.yaml
	services/gtfs/
		deployment.yaml
		service.yaml
		kustomization.yaml
	vault/
		clustersecretstore.yaml
		externalsecret-gtfs.yaml
		kustomization.yaml

terraform/
	providers.tf
	variables.tf
	main.tf
	outputs.tf
	terraform.tfvars.example
	values/
```

## Step-by-step dev/test setup (local machine)

**Recommended: Read [KIND-SETUP.md](KIND-SETUP.md) for automated cluster bootstrap.**

### 1) Prerequisites

Install:

1. Docker Desktop - https://www.docker.com/products/docker-desktop
2. kind - `choco install kind` or `brew install kind`
3. kubectl - `choco install kubernetes-cli` or `brew install kubectl`
4. Helm 3 - `choco install helm` or `brew install helm`
5. Terraform >= 1.7 - `choco install terraform` or `brew install terraform`
6. Python 3.10+ (for pre-commit and GTFS development)

### 2) Create Local Cluster with kind

**Windows PowerShell:**
```powershell
.\kind-cluster-setup.ps1
```

**macOS/Linux:**
```bash
chmod +x kind-cluster-setup.sh
./kind-cluster-setup.sh
```

This creates a single-node Kubernetes cluster in Docker, ideal for dev/test.

### 3) Configure pre-commit hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Hooks now include:

1. secret detection (gitleaks + private key detection)
2. yaml/json/basic hygiene checks
3. Python flake8 checks for GTFS
4. Dockerfile linting

### 4) Configure GitHub secrets and variables

Set these repository secrets:

1. `DISCORD_WEBHOOK_URL`
2. `POSTGRES_USER`
3. `POSTGRES_PASSWORD`
4. `POSTGRES_DB`

No PAT is needed for GHCR push because workflow uses `GITHUB_TOKEN` with `packages: write`.

### 5) Bootstrap platform addons with Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

This installs:

1. ingress-nginx
2. kube-prometheus-stack (Prometheus/Grafana/Alertmanager)
3. Loki
4. Vault
5. External Secrets Operator
6. Argo CD

### 6) Initialize Vault for External Secrets

After Vault is installed (dev mode in this setup):

1. port-forward Vault UI/API
2. enable Kubernetes auth method in Vault
3. create policy `external-secrets` allowing read on `secret/data/gtfs`
4. create role `external-secrets` bound to SA `external-secrets` in namespace `external-secrets`
5. write GTFS secret values to Vault path `secret/data/gtfs`

Example values expected by `gitops/vault/externalsecret-gtfs.yaml`:

1. `POSTGRES_USER`
2. `POSTGRES_PASSWORD`
3. `POSTGRES_DB`
4. `POSTGRES_PORT`

### 7) Apply Argo CD application

Apply:

```bash
kubectl apply -f gitops/environments/dev/gtfs-application.yaml -n argocd
```

Argo CD will sync `gitops/` to cluster and create:

1. GTFS Deployment/Service
2. Ingress for GTFS
3. Vault ExternalSecret resources

### 8) Configure Cloudflare Tunnel to ingress

1. Create Cloudflare Tunnel on your machine.
2. Route hostname (for example `gtfs-dev.example.com`) to local ingress endpoint.
3. Keep `gitops/ingress/ingress.yaml` host aligned with your Cloudflare DNS hostname.

### 9) Verify observability and notifications

1. Check Prometheus targets are up.
2. Open Grafana and import dashboards.
3. Confirm Loki receives logs.
4. Trigger a test alert and verify Discord webhook receives it.

## CI/CD lifecycle (what happens on every change)

1. Developer commits code.
2. Pre-commit blocks bad commits locally.
3. Push/PR triggers GTFS CI in `.github/workflows/gtfs.yaml`.
4. CI runs secret scan, lint, tests, smoke test, and sends Discord status.
5. Push to `main` triggers CD in `.github/workflows/deploy.yml`.
6. CD builds `services/gtfs` image and pushes to `ghcr.io/<owner>/gtfs:<sha>`.
7. CD updates `gitops/services/gtfs/deployment.yaml` image tag and commits.
8. Argo CD syncs desired state from `gitops/` to the cluster.
9. Monitoring and alerts report health to Grafana/Prometheus/Loki and Discord.

## Ingress and GTFS service notes

1. Ingress file: `gitops/ingress/ingress.yaml`
2. Service file: `gitops/services/gtfs/service.yaml`
3. Deployment file: `gitops/services/gtfs/deployment.yaml`

If you change GTFS port, update Deployment, Service, and Ingress together.

## Moving to Azure production later (easy transition)

You can keep the same GitOps and app manifests. Main changes:

1. switch cluster target from local k3s to AKS
2. switch Vault option to Azure Key Vault integration (or keep Vault if preferred)
3. keep GHCR or move to ACR
4. keep Argo CD and the same `gitops/` structure
5. update DNS/ingress to production domain and WAF

## Operational checklist

1. `pre-commit run --all-files` passes
2. `GTFS CI` workflow is green
3. `Build and Deploy GTFS (GitOps)` workflow is green
4. Argo CD app is Synced and Healthy
5. GTFS ingress endpoint is reachable via Cloudflare hostname
6. Grafana, Prometheus, and Loki are receiving data
7. Discord receives CI/CD and alert notifications
