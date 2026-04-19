# Colonel-Sanders-CGMplus

## Проблем

CGM Plus е мобилно приложение, което цели да улесни използването на градският транспорт в София чрез обединение на множество функции, като дигитална карта за превоз; карта със всички спирки и реалното положение на автобусите, тролейбусите и трамваите; актуална информация за потребителя и градския транспорт, и др. - всичко на едно място.
Това приложение би могло да реши често срещани проблеми от пътниците на градския транспорт, като забравянето на картата за превоз или пък незнание кога тя изтича, което често води до возене “гратис” в превозното средство. Друг проблем е неяснота по кога твоето превозно средство ще пристигне на спирката - на таблото може да пише, че пристига след “0” минути, но след това да изпише, че всъщност идва след “1” минута и реално да дойде след 5. С приложението, потребителят може да провери точното местоположение на превозното средство, да види с каква скорост се движи, ако въобще се движи (може да е спрял на спирка или светофар), в коя посока се движи и колко е натоварено вътре в превозното средство.
Отделно, приложението разполага с чисто нова функция “лоялна програма”, която има за цел да стимулира хората да използват повече градски транспорт, вместо собственият си автомобил, като чрез редовно използване, те трупат точки, които след това могат да бъдат въведени в безплатни карти за превоз.

## Architectural Diagram
[Here](/docs/ArchitecturalDiagram.png)

## Used Technologies

### Backend
Python 3.12, 3.13
Flask 3.0.2
Marshmallow 3.21.0
PostgreSQL 16
ArgoCD
Terraform

### Frontend
Expo 54.0.33
React 19.1.0

## Api docs
[Api docs](/docs/api/)


## Aditional stuff


This repository is currently configured for local development with only core runtime components:

- GTFS service
- Auth service
- Auth Postgres database
- NGINX ingress controller

No local observability stack is included in this mode (no Prometheus, Grafana, Loki, or Promtail).

## Local Architecture

- [docker-compose.yaml](docker-compose.yaml): starts the local stack
- [ops/local/nginx/nginx.conf](ops/local/nginx/nginx.conf): ingress routing rules
- [services/gtfs](services/gtfs): GTFS service source and Docker build
- [services/auth-new](services/auth-new): Auth service source and Docker build

## Ports

- `8080` -> ingress entrypoint (all API traffic should go through this)
- `5432` -> used internally by `auth-db` container (not published to host)
- `5000` -> used internally by `gtfs` and `auth` containers (not published to host)

Only `8080` is exposed on the host machine.

## Local Routes Through Ingress

All requests should go to `http://localhost:8080`.

- `/auth/*` -> Auth service
- `/users/*` -> Auth service
- `/health/auth` -> Auth health check (`/health`)
- `/api/v1/*` -> GTFS service
- `/health/` -> GTFS health check
- `/` -> GTFS root/docs route

## Environment Variables

Create a root `.env` file (not committed) with at least:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `JWT_SECRET`

Example values:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=auth_db
JWT_SECRET=local-dev-jwt-secret
```

## Run Local Dev

```bash
docker compose up --build -d
```

## Verify

- `http://localhost:8080/health/` should return GTFS health
- `http://localhost:8080/health/auth` should return Auth health

## Stop

```bash
docker compose down
```

To also remove the auth database volume:

```bash
docker compose down -v
```

## GitOps Branch Model

- `development`: dev/test environment branch (minikube cluster on hosted PC)
- `main`: production environment branch (Azure target)

Argo CD applications:

- Dev app manifest: [gitops/environments/dev/CGMplus-dev.yaml](gitops/environments/dev/CGMplus-dev.yaml)
	: tracks `development`
- Prod app manifest: [gitops/environments/prod/CGMplus-prod.yaml](gitops/environments/prod/CGMplus-prod.yaml)
	: tracks `main`

Overlay paths:

- Dev overlay: `gitops/environments/dev/manifests` (includes Vault-backed external secrets)
- Prod overlay: `gitops/environments/prod/manifests` (includes Azure Key Vault-backed external secrets)

## Cluster Dev/Test Flow (minikube + Cloudflare)

1. Push code to `development`.
2. CI runs service tests from [GTFS CI workflow](.github/workflows/gtfs.yaml) and [AUTH CI workflow](.github/workflows/auth.yml).
3. Build pipeline [deploy workflow](.github/workflows/deploy.yml):
	 - builds/pushes `docker.io/<dockerhub-username>/gtfs:<sha>`
	 - builds/pushes `docker.io/<dockerhub-username>/auth-new:<sha>`

	 Required GitHub repository secrets for image publish:
	 - `DOCKERHUB_USERNAME`
	 - `DOCKERHUB_TOKEN` (Docker Hub access token)
	 - updates GitOps deployment image tags in the same branch
4. Argo CD in test cluster detects GitOps manifest change in `development` and syncs.
5. Cloudflare Tunnel exposes ingress host publicly for testing.

## Secrets Model

- Dev/test: Vault + External Secrets in minikube cluster.
- Production: Azure-managed secrets (for example Key Vault) is the target model.

Current production backend manifests:

- `gitops/azure-secrets/clustersecretstore-azurekv.yaml`
- `gitops/azure-secrets/externalsecret-auth.yaml`

## Terraform By Environment

Use environment-specific tfvars examples:

- `terraform/dev.tfvars.example` (Vault enabled)
- `terraform/prod.tfvars.example` (Vault disabled)

Apply to production AKS after `az aks get-credentials`:

```bash
cd terraform
cp prod.tfvars.example prod.tfvars
terraform init
terraform plan -var-file=prod.tfvars
terraform apply -var-file=prod.tfvars
```

Then apply production Argo CD app:

```bash
kubectl apply -f gitops/environments/prod/CGMplus-prod.yaml -n argocd
```

Current ExternalSecret manifests:

- GTFS: [gitops/vault/externalsecret-gtfs.yaml](gitops/vault/externalsecret-gtfs.yaml)
- Auth: [gitops/vault/externalsecret-auth.yaml](gitops/vault/externalsecret-auth.yaml)

For detailed minikube bootstrap and Cloudflare steps, see [MINIKUBE-SETUP.md](MINIKUBE-SETUP.md).
