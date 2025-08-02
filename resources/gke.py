from cdktf import TerraformModule

def create_gke_clusters(scope, project_id, gke_list, all_modules):
    gke_outputs = {}

    for gke_cfg in gke_list:
        gke_name = gke_cfg["name"]
        vpc_name = gke_cfg["vpc_name"]
        subnet_name = gke_cfg["subnetwork"]

        gke_module = TerraformModule(
            scope,
            f"gke-{gke_name}",
            source="git::https://github.com/anoopdevopseng/terraform-google-gke?ref=v0.1.0",
        )

        gke_module.add_override("project_id", project_id)
        gke_module.add_override("name", gke_name)
        gke_module.add_override("environment", gke_cfg["environment"])
        gke_module.add_override("location", gke_cfg["location"])
        gke_module.add_override("vpc_name", vpc_name)
        gke_module.add_override("subnetwork", subnet_name)
        gke_module.add_override("deletion_protection", gke_cfg.get("deletion_protection", False))
        gke_module.add_override("enable_private_endpoint", gke_cfg.get("enable_private_endpoint", False))
        gke_module.add_override("master_global_access_config", gke_cfg.get("master_global_access_config", True))
        gke_module.add_override("gcp_public_cidrs_access_enabled", gke_cfg.get("gcp_public_cidrs_access_enabled", True))
        gke_module.add_override("cluster_secondary_range_name", gke_cfg["cluster_secondary_range_name"])
        gke_module.add_override("services_secondary_range_name", gke_cfg["services_secondary_range_name"])
        gke_module.add_override("node_pools", gke_cfg["node_pools"])
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
