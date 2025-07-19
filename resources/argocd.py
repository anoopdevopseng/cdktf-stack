from constructs import Construct
from cdktf import TerraformModule, TerraformModuleProvider

from cdktf_cdktf_provider_google.data_google_client_config import DataGoogleClientConfig

from imports.kubernetes.provider import KubernetesProvider
from imports.helm.provider import HelmProvider

def setup_argocd_if_enabled(scope: Construct, gke_cfg: dict, gke_module: TerraformModule):
    gke_name = gke_cfg["name"]

    if not gke_cfg.get("argocd", False):
        return None

    google_client_config = DataGoogleClientConfig(scope, "default")
    dns_external = gke_cfg.get("dns_allow_external_traffic", False)
    provider_alias = f"{gke_name}-argocd"

    endpoint_output = f"${{module.{gke_module.friendly_unique_id}.endpoint}}"
    token_output = "${data.google_client_config.default.access_token}"

    ca_cert_output = None
    if not dns_external:
        ca_cert_output = f"${{base64decode(module.{gke_module.friendly_unique_id}.master_auth[0].cluster_ca_certificate)}}"

    def build_k8s_config():
        config = {
            "host": f"https://{endpoint_output}",
            "token": token_output,
        }
        if ca_cert_output:
            config["cluster_ca_certificate"] = ca_cert_output
        return config

    # Kubernetes provider
    k8s_provider = KubernetesProvider(
        scope,
        f"kubernetes-{gke_name}",
        alias=provider_alias,
        **build_k8s_config()
    )

    # Helm provider
    helm_provider = HelmProvider(
        scope,
        f"helm-{gke_name}",
        alias=provider_alias,
        kubernetes=build_k8s_config()
    )

    # ArgoCD Helm module
    argocd_module = TerraformModule(
        scope,
        f"argocd-{gke_name}",
        source="git::https://github.com/anoopdevopseng/terraform-helm-argocd.git?ref=v0.1.0",
        providers=[
            TerraformModuleProvider(
                module_alias="helm",
                provider=helm_provider
            ),
            TerraformModuleProvider(
                module_alias="kubernetes",
                provider=k8s_provider
            )
        ]
    )

    # Set module input
    argocd_module.add_override("namespace", "argocd")

    return argocd_module