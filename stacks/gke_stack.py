from constructs import Construct
from cdktf import TerraformStack, TerraformModule, TerraformOutput
from cdktf_cdktf_provider_google.provider import GoogleProvider


class GkeStack(TerraformStack):
    def __init__(self, scope: Construct, id: str, project_id: str, region: str, gke_list: list, all_modules: dict):
        super().__init__(scope, id)

        # Configure Google Provider
        GoogleProvider(self, "google", project=project_id, region=region)

        # Create GKE clusters
        self.gke_outputs = {}

        for gke_cfg in gke_list:
            gke_name = gke_cfg["name"]
            vpc_name = gke_cfg["vpc_name"]
            subnet_name = gke_cfg["subnetwork"]

            gke_module = TerraformModule(
                self,
                f"gke-{gke_name}",
                source="terraform-google-gke",
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

            self.gke_outputs[gke_name] = gke_module

        # Create outputs for each GKE cluster matching the original module structure
        for gke_name, gke_module in self.gke_outputs.items():
            # Name output - matches original "name" output
            TerraformOutput(
                self,
                f"{gke_name}_name",
                value=gke_module.get_string("name"),
                description=f"Name of GKE cluster {gke_name}"
            )
            
            # Location output - matches original "location" output
            TerraformOutput(
                self,
                f"{gke_name}_location",
                value=gke_module.get_string("location"),
                description=f"Location of GKE cluster {gke_name}"
            )
            
            # Endpoint output - matches original "endpoint" output
            TerraformOutput(
                self,
                f"{gke_name}_endpoint",
                value=gke_module.get_string("endpoint"),
                description=f"Endpoint of GKE cluster {gke_name}"
            )
            
            # Master auth output - matches original "master_auth" output
            TerraformOutput(
                self,
                f"{gke_name}_master_auth",
                value=gke_module.get_string("master_auth"),
                description=f"Master authentication for GKE cluster {gke_name}",
                sensitive=True
            )
            
            # Node pool output - matches original "node_pool" output
            TerraformOutput(
                self,
                f"{gke_name}_node_pool",
                value=gke_module.get_string("node_pool"),
                description=f"Node pool for GKE cluster {gke_name}"
            ) 