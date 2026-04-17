variable "kubeconfig_path" {
  description = "Path to kubeconfig used by Terraform (k3s for dev/test or AKS for production)."
  type        = string
  default     = "~/.kube/config"
}

variable "discord_webhook_url" {
  description = "Discord webhook URL used by Alertmanager for observability notifications."
  type        = string
  sensitive   = true
  default     = ""
}

variable "enable_argocd" {
  description = "Enable Argo CD installation."
  type        = bool
  default     = true
}

variable "enable_vault" {
  description = "Enable HashiCorp Vault installation."
  type        = bool
  default     = true
}

variable "enable_external_secrets" {
  description = "Enable External Secrets Operator installation."
  type        = bool
  default     = true
}

variable "enable_observability" {
  description = "Enable Prometheus, Grafana, and Loki stack installation."
  type        = bool
  default     = true
}
