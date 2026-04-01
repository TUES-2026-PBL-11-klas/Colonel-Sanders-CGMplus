# Bootstrap minikube dev/test cluster for CGMplus
$ClusterName = "cgmplus-dev"
$BaseImage = "gcr.io/k8s-minikube/kicbase:v0.0.50"

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
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Host "Docker CLI not found. Install Docker Desktop before continuing." -ForegroundColor Red
  exit 1
}

Write-Host "[2] Pre-pulling minikube base image to avoid long silent waits..." -ForegroundColor Green
docker pull $BaseImage
if ($LASTEXITCODE -ne 0) {
  Write-Host "Failed to pull $BaseImage. Check Docker Desktop and network/proxy settings." -ForegroundColor Red
  exit $LASTEXITCODE
}

Write-Host "[3] Starting minikube profile '$ClusterName' (this takes 2-5 minutes)..." -ForegroundColor Green
$startTime = Get-Date
minikube start -p $ClusterName --driver=docker --cpus=4 --memory=8192
if ($LASTEXITCODE -ne 0) {
  Write-Host "Initial start failed. Recreating profile '$ClusterName' and retrying once..." -ForegroundColor Yellow
  minikube delete -p $ClusterName
  minikube start -p $ClusterName --driver=docker --cpus=4 --memory=8192
  if ($LASTEXITCODE -ne 0) {
    Write-Host "minikube start failed after retry. Run: minikube logs -p $ClusterName" -ForegroundColor Red
    exit $LASTEXITCODE
  }
}
Write-Host ("minikube start completed in {0:n1} minutes" -f (((Get-Date) - $startTime).TotalMinutes)) -ForegroundColor DarkGray

minikube -p $ClusterName update-context
if ($LASTEXITCODE -ne 0) {
  Write-Host "Failed to update kube context for '$ClusterName'." -ForegroundColor Red
  exit $LASTEXITCODE
}

Write-Host "[4] Verifying cluster..." -ForegroundColor Green
kubectl cluster-info
if ($LASTEXITCODE -ne 0) {
  Write-Host "kubectl cluster-info failed. Check current context and minikube status." -ForegroundColor Red
  exit $LASTEXITCODE
}
kubectl get nodes
if ($LASTEXITCODE -ne 0) {
  Write-Host "kubectl get nodes failed." -ForegroundColor Red
  exit $LASTEXITCODE
}

Write-Host "[5] minikube cluster is ready for Terraform + Argo CD bootstrap" -ForegroundColor Green
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
