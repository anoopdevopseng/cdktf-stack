import os
import sys
import yaml
from cdktf import App

from config.utils import load_config
from stacks import VpcStack, NatStack, GkeStack

# --- Load YAML config ---
env = os.getenv("ENV")
if not env:
    raise Exception("ENV variable not set. Run with: ENV=dev python main.py")

yaml_path = f"envs/{env}.yaml"
config = load_config(yaml_path)

# --- CDKTF App ---
app = App()
try:
    project_id = config["project_id"]
    region = config.get("region", "europe-west3")

    # Create VPC Stack
    print(f"Creating VPC stack for environment: {env}")
    vpc_stack = VpcStack(app, f"vpc-stack-{env}", project_id, region, config.get("vpcs", []))
    
    # Create NAT Stack (depends on VPC)
    print(f"Creating NAT stack for environment: {env}")
    nat_stack = NatStack(app, f"nat-stack-{env}", project_id, region, config.get("nats", []), vpc_stack.all_modules)
    
    # Create GKE Stack (depends on VPC and NAT)
    print(f"Creating GKE stack for environment: {env}")
    all_modules = {**vpc_stack.all_modules, **nat_stack.all_modules}
    gke_stack = GkeStack(app, f"gke-stack-{env}", project_id, region, config.get("gke_clusters", []), all_modules)
    
    print(f"Synthesizing CDKTF app for environment: {env}")
    app.synth()
    print(f"Successfully created and synthesized all stacks for environment: {env}")
    print(f"Stack Summary:")
    print(f"   - VPC Stack: {len(vpc_stack.vpc_outputs)} VPCs created")
    print(f"   - NAT Stack: {len(nat_stack.nat_modules)} NAT Gateways created")
    print(f"   - GKE Stack: {len(gke_stack.gke_outputs)} GKE clusters created")
    
except Exception as e:
    print(f"\nError: {e}", file=sys.stderr)
    sys.exit(1)
