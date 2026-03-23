@echo off
REM kind-cluster-setup.bat
REM Windows PowerShell version

$ClusterName = "gtfs-dev"

Write-Host "[1] Creating kind cluster configuration..." -ForegroundColor Green
$KindConfig = @"
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: $ClusterName
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 80
        hostPort: 80
      - containerPort: 443
        hostPort: 443
"@

$KindConfig | Out-File -FilePath "kind-config.yaml" -Encoding UTF8

Write-Host "[2] Creating kind cluster (this takes 1-2 minutes)..." -ForegroundColor Green
try {
  kind create cluster --config=kind-config.yaml
} catch {
  Write-Host "Cluster might already exist. Attempting to delete and recreate..." -ForegroundColor Yellow
  kind delete cluster --name=$ClusterName -ErrorAction SilentlyContinue
  kind create cluster --config=kind-config.yaml
}

Write-Host "[3] Verifying cluster..." -ForegroundColor Green
kubectl cluster-info
kubectl get nodes

Write-Host "[4] Checking Helm..." -ForegroundColor Green
if (-not (Get-Command helm -ErrorAction SilentlyContinue)) {
  Write-Host "Helm not found. Install from https://helm.sh/docs/intro/install/" -ForegroundColor Red
  exit 1
}

Write-Host "[5] Ready for Terraform apply!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. cd terraform"
Write-Host "  2. cp terraform.tfvars.example terraform.tfvars"
Write-Host "  3. Edit terraform.tfvars (set discord_webhook_url)"
Write-Host "  4. terraform init"
Write-Host "  5. terraform apply"
Write-Host ""
Write-Host "Cluster kubeconfig already configured in ~/.kube/config" -ForegroundColor Cyan
