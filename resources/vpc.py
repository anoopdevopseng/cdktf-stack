from cdktf import TerraformModule
from imports.vpc import Vpc as vpc

def create_vpcs(scope, project_id, vpc_list):
    vpc_outputs = {}
    all_modules = {}

    for vpc_cfg in vpc_list:
        vpc_name = vpc_cfg["name"]
        subnets_input = {
            name: {
                "ip_range": val["ip_range"],
                "private_ip_google_access": val.get("private_ip_google_access", False),
                "secondary_ip_ranges": val.get("secondary_ip_ranges", [])
            }
            for name, val in vpc_cfg.get("subnets", {}).items()
        }

        vpc_module = vpc(
            scope,
            f"vpc-{vpc_name}",
            project_id=project_id,
            name=vpc_name,
            subnets=subnets_input
        )
        vpc_module.add_override("routing_mode", vpc_cfg.get("routing_mode", "REGIONAL"))

        vpc_outputs[vpc_name] = vpc_module
        all_modules[vpc_name] = vpc_module

    return vpc_outputs, all_modules