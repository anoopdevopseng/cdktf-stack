import os
import sys
import yaml
from constructs import Construct
from cdktf import App, TerraformStack
from cdktf_cdktf_provider_google.provider import GoogleProvider

from resources.utils import load_config
from resources.vpc import create_vpcs
from resources.gke import create_gke_clusters

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str, config: dict):
        super().__init__(scope, id)

        project_id = config["project_id"]
        region = config.get("region", "europe-west3")

        GoogleProvider(self, "google", project=project_id, region=region)

        # Create VPCs
        vpc_outputs, all_modules = create_vpcs(self, project_id, config.get("vpcs", []))

        # Create GKE clusters
        gke_outputs = create_gke_clusters(self, project_id, config.get("gke_clusters", []), all_modules)


# --- Load YAML config ---
env = os.getenv("ENV")
if not env:
    raise Exception("ENV variable not set. Run with: ENV=dev python main.py")

yaml_path = f"envs/{env}.yaml"
config = load_config(yaml_path)

# --- CDKTF App ---
app = App()
try:
    MyStack(app, f"application-stack-{env}", config)
    app.synth()
except Exception as e:
    print(f"\n{e}", file=sys.stderr)
    sys.exit(1)
