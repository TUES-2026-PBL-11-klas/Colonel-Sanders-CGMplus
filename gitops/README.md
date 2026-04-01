# GitOps Layout

This folder mirrors the baseline structure from the external GitOps repository and is used by Argo CD/Flux.

- environments/dev and environments/prod contain environment-level app definitions.
- ingress contains shared ingress resources.
- services/gtfs contains GTFS workload manifests.
- services/auth contains Auth workload manifests.
- vault contains External Secrets resources that pull app secrets from HashiCorp Vault.

Branch tracking model:

- dev application tracks `development`
- prod application tracks `main`
