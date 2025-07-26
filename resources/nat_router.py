from cdktf import TerraformModule
from cdktf_cdktf_provider_google.data_google_compute_network import DataGoogleComputeNetwork


def create_nats(scope, project_id, nat_list,vpc_modules):
    nat_modules = {}
    all_modules = {}

    for nat_cfg in nat_list:
        env = nat_cfg["environment"]
        vpc_name = nat_cfg["vpc_id"]

        if vpc_name in vpc_modules:
            # VPC is defined internally
            vpc_module = vpc_modules[vpc_name]
            vpc_self_link = vpc_module.output["vpc"]["self_link"]

            nat_module = TerraformModule(
                scope,
                f"{vpc_name}-nat-{env}",
                source="git::https://github.com/anoopdevopseng/terraform-google-cloudnat?ref=v0.1.0"
            )

            nat_module.add_override("project_id", project_id)
            nat_module.add_override("environment", env)
            nat_module.add_override("region", nat_cfg["region"])
            nat_module.add_override("vpc_id", vpc_self_link)
            nat_module.add_override("num_nat_ips", nat_cfg.get("num_nat_ips", 1))
            nat_module.add_override("subnet_ids_to_nat", nat_cfg["subnet_ids_to_nat"])

            nat_module.add_override("depends_on", [vpc_module.fqn])

            nat_modules[env] = nat_module
            all_modules[env] = nat_module
        
        else:
        # Lookup VPC self_link by name
            vpc_lookup = DataGoogleComputeNetwork(
                scope,
                f"{vpc_name}-{env}",
                name=vpc_name,
                project=project_id
            )
            nat_module = TerraformModule(
                scope,
                f"{vpc_name}-nat-{env}",
                source="git::https://github.com/anoopdevopseng/terraform-google-cloudnat?ref=v0.1.0"
            )
            nat_module.add_override("project_id", project_id)
            nat_module.add_override("environment", env)
            nat_module.add_override("region", nat_cfg["region"])
            nat_module.add_override("vpc_id", vpc_lookup.self_link)
            nat_module.add_override("num_nat_ips", nat_cfg.get("num_nat_ips", 1))
            nat_module.add_override("subnet_ids_to_nat", nat_cfg["subnet_ids_to_nat"])

            nat_modules[env] = nat_module
            all_modules[env] = nat_module

    return nat_modules, all_modules