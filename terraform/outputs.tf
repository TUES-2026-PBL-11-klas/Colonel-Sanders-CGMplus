output "installed_addons" {
  description = "Installed platform addons."
  value       = keys(helm_release.addons)
}
