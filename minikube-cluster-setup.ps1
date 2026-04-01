# Bootstrap minikube dev/test cluster for CGMplus
$ClusterName = "cgmplus-dev"

Write-Host "[1] Checking prerequisites..." -ForegroundColor Green
if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) {
  Write-Host "minikube not found. Install from https://minikube.sigs.k8s.io/docs/start/" -ForegroundColor Red
  exit 1
}
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
  Write-Host "kubectl not found. Install kubectl before continuing." -ForegroundColor Red
  exit 1
}
if (-not (Get-Command helm -ErrorAction SilentlyContinue)) {
  Write-Host "Helm not found. Install from https://helm.sh/docs/intro/install/" -ForegroundColor Red
  exit 1
}

Write-Host "[2] Starting minikube profile '$ClusterName' (this takes 2-5 minutes)..." -ForegroundColor Green
minikube start -p $ClusterName --driver=docker --cpus=4 --memory=8192
minikube -p $ClusterName update-context

Write-Host "[3] Verifying cluster..." -ForegroundColor Green
kubectl cluster-info
kubectl get nodes

Write-Host "[4] minikube cluster is ready for Terraform + Argo CD bootstrap" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. cd terraform"
Write-Host "  2. cp terraform.tfvars.example terraform.tfvars"
Write-Host "  3. Edit terraform.tfvars and keep enable_argocd/enable_vault/enable_external_secrets = true"
Write-Host "  4. terraform init"
Write-Host "  5. terraform apply"
Write-Host "  6. kubectl apply -f ../gitops/environments/dev/CGMplus-dev.yaml -n argocd"
Write-Host ""
Write-Host "Cloudflare for test access:" -ForegroundColor Cyan
Write-Host "  - Run: kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80"
Write-Host "  - Then: cloudflared tunnel run cgmplus-dev --url http://localhost:8080"
