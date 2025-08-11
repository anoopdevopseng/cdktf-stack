from cdktf import TerraformModule
from imports.gke import Gke as gke

def create_gke_clusters(scope, project_id, gke_list, all_modules):
    gke_outputs = {}

    for gke_cfg in gke_list:
        gke_name = gke_cfg["name"]
        vpc_name = gke_cfg["vpc_name"]
        subnet_name = gke_cfg["subnetwork"]

        gke_module = gke(
            scope,
            f"gke-{gke_name}",
            project_id=project_id,
            environment=gke_cfg["environment"],
            name=gke_name,
            node_pools=gke_cfg["node_pools"],
            services_secondary_range_name=gke_cfg["services_secondary_range_name"],
            cluster_secondary_range_name=gke_cfg["cluster_secondary_range_name"]
        )

        gke_module.add_override("location", gke_cfg["location"])
        gke_module.add_override("vpc_name", vpc_name)
        gke_module.add_override("subnetwork", subnet_name)
        gke_module.add_override("deletion_protection", gke_cfg.get("deletion_protection", False))
        gke_module.add_override("enable_private_endpoint", gke_cfg.get("enable_private_endpoint", False))
        gke_module.add_override("master_global_access_config", gke_cfg.get("master_global_access_config", True))
        gke_module.add_override("gcp_public_cidrs_access_enabled", gke_cfg.get("gcp_public_cidrs_access_enabled", True))
        gke_module.add_override("argocd", gke_cfg.get("argocd", False))
        if "dns_allow_external_traffic" in gke_cfg:
            gke_module.add_override("dns_allow_external_traffic", gke_cfg["dns_allow_external_traffic"])

        # Check dependencies
        depends_on_names = gke_cfg.get("depends_on", [])
        depends_on_paths = []
        for dep in depends_on_names:
            if dep not in all_modules:
                raise Exception(f"GKE '{gke_name}' depends on unknown module '{dep}'. Please define it earlier in your config.")
            depends_on_paths.append(f"module.{all_modules[dep].node.id}")

        if depends_on_paths:
            gke_module.add_override("depends_on", depends_on_paths)

        gke_outputs[gke_name] = gke_module

    return gke_outputs
