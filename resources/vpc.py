from cdktf import TerraformModule

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

        vpc_module = TerraformModule(
            scope,
            f"vpc-{vpc_name}",
            source="git::https://github.com/anoopdevopseng/terraform-google-vpc?ref=v0.1.0",
        )

        vpc_module.add_override("project_id", project_id)
        vpc_module.add_override("name", vpc_name)
        vpc_module.add_override("routing_mode", vpc_cfg.get("routing_mode", "REGIONAL"))
        vpc_module.add_override("subnets", subnets_input)

        vpc_outputs[vpc_name] = vpc_module
        all_modules[vpc_name] = vpc_module

    return vpc_outputs, all_modules