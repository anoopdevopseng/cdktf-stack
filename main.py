#!/usr/bin/env python
import os
import sys
import yaml
from constructs import Construct
from cdktf import App, TerraformStack, TerraformModule
from cdktf_cdktf_provider_google.provider import GoogleProvider


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str, config: dict):
        super().__init__(scope, id)

        # Shared project and region
        project_id = config["project_id"]
        region = config.get("region", "europe-west3")

        GoogleProvider(self, "google", project=project_id, region=region)

        vpc_outputs = {}
        all_modules = {}

        # === Create VPCs ===
        for vpc_cfg in config.get("vpcs",[]):
            vpc_name = vpc_cfg["name"]

            # Convert subnets YAML to module input format
            subnets_input = {}
            for subnet_name, subnet_cfg in vpc_cfg["subnets"].items():
                subnets_input[subnet_name] = {
                    "ip_range": subnet_cfg["ip_range"],
                    "private_ip_google_access": subnet_cfg.get("private_ip_google_access", False),
                    "secondary_ip_ranges": subnet_cfg.get("secondary_ip_ranges", [])
                }

            # Create VPC module
            vpc_module = TerraformModule(
                self,
                f"vpc-{vpc_name}",
                source="git::https://github.com/anoopdevopseng/terraform-google-vpc?ref=v0.1.0",
            )

            vpc_module.add_override("project_id", project_id)
            vpc_module.add_override("name", vpc_name)
            vpc_module.add_override("routing_mode", vpc_cfg.get("routing_mode", "REGIONAL"))
            vpc_module.add_override("subnets", subnets_input)

            vpc_outputs[vpc_name] = vpc_module
            all_modules[vpc_name] = vpc_module

        # Setup the gke 
        for gke_cfg in config.get("gke_clusters", []):
            gke_name = gke_cfg["name"]
            vpc_name = gke_cfg["vpc_name"]
            subnet_name = gke_cfg["subnetwork"]

            gke_module = TerraformModule(
                self,
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

            # Handle depends_on if declared
            depends_on_names = gke_cfg.get("depends_on", [])
            depends_on_paths = []

            for dep_name in depends_on_names:
                if dep_name not in all_modules:
                    raise Exception(f"GKE '{gke_name}' depends on unknown module '{dep_name}'. Please define it earlier in your config.")
                depends_on_paths.append(f"module.{all_modules[dep_name].node.id}")

            if depends_on_paths:
                gke_module.add_override("depends_on", depends_on_paths)

# --- Load YAML config ---
env = os.getenv("ENV")
if not env:
    raise Exception("ENV variable not set. Run with: ENV=dev python main.py")

yaml_path = f"envs/{env}.yaml"
if not os.path.exists(yaml_path):
    raise FileNotFoundError(f"Config file not found: {yaml_path}")

with open(yaml_path) as f:
    config = yaml.safe_load(f)

# --- CDKTF App ---
app = App()
try:
    MyStack(app, f"application-stack-{env}", config)
    app.synth()
except Exception as e:
    print(f"\n{e}", file=sys.stderr)  # <-- Send error to stderr, not stdout
    sys.exit(1)
