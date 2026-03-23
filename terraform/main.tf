locals {
  namespaces = toset([
    "argocd",
    "external-secrets",
    "gtfs",
    "ingress-nginx",
    "monitoring",
    "vault",
  ])

  addons = {
    ingress-nginx = {
      enabled     = true
      namespace   = "ingress-nginx"
      repository  = "https://kubernetes.github.io/ingress-nginx"
      chart       = "ingress-nginx"
      version     = "4.11.3"
      values_file = "${path.module}/values/ingress-nginx.yaml"
    }
    kube-prometheus-stack = {
      enabled     = var.enable_observability
      namespace   = "monitoring"
      repository  = "https://prometheus-community.github.io/helm-charts"
      chart       = "kube-prometheus-stack"
      version     = "62.7.0"
      values_file = "${path.module}/values/kube-prometheus-stack.tftpl"
    }
    loki = {
      enabled     = var.enable_observability
      namespace   = "monitoring"
      repository  = "https://grafana.github.io/helm-charts"
      chart       = "loki"
      version     = "6.16.0"
      values_file = "${path.module}/values/loki.yaml"
    }
    vault = {
      enabled     = var.enable_vault
      namespace   = "vault"
      repository  = "https://helm.releases.hashicorp.com"
      chart       = "vault"
      version     = "0.28.1"
      values_file = "${path.module}/values/vault.yaml"
    }
    external-secrets = {
      enabled     = var.enable_external_secrets
      namespace   = "external-secrets"
      repository  = "https://charts.external-secrets.io"
      chart       = "external-secrets"
      version     = "0.10.5"
      values_file = "${path.module}/values/external-secrets.yaml"
    }
    argocd = {
      enabled     = var.enable_argocd
      namespace   = "argocd"
      repository  = "https://argoproj.github.io/argo-helm"
      chart       = "argo-cd"
      version     = "7.7.11"
      values_file = "${path.module}/values/argocd.yaml"
    }
  }

  enabled_addons = {
    for name, addon in local.addons : name => addon if addon.enabled
  }
}

resource "kubernetes_namespace" "namespaces" {
  for_each = local.namespaces

  metadata {
    name = each.value
  }
}

resource "helm_release" "addons" {
  for_each = local.enabled_addons

  name             = each.key
  namespace        = each.value.namespace
  repository       = each.value.repository
  chart            = each.value.chart
  version          = each.value.version
  create_namespace = true
  timeout          = 1200
  wait             = true
  wait_for_jobs    = false

  values = [
    each.key == "kube-prometheus-stack"
    ? templatefile(each.value.values_file, { discord_webhook_url = var.discord_webhook_url })
    : file(each.value.values_file)
  ]

  depends_on = [kubernetes_namespace.namespaces]
}
