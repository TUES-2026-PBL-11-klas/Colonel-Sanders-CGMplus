# Colonel-Sanders-CGMplus
A better app for the public transportaion in Sofia, Sofia-grad, Bulgaria
## Development environment

### Prerequisites
- Docker
- Minikube
- Kubectl
- Python 3.9+ (for pre-commit)

### Pre-commit hooks

This repository uses `pre-commit` hooks to run lightweight checks before each commit.

#### One-time setup

```bash
pip install pre-commit
pre-commit install
```

#### Run hooks manually

```bash
pre-commit run --all-files
```

Hook configuration is defined in `.pre-commit-config.yaml`.

#### Start the development cluster
```
minikube start --driver=docker
```
