from constructs import Construct
from cdktf import TerraformModule
from cdktf_cdktf_provider_google.data_google_compute_network import DataGoogleComputeNetwork
from imports.nat import Nat as nat_router


def create_nats(scope, project_id, nat_list,vpc_modules):
    nat_modules = {}
    all_modules = {}

    for nat_cfg in nat_list:
        env = nat_cfg["environment"]
        vpc_name = nat_cfg["vpc_id"]

        depends_on = []
        
        # Lookup VPC self_link by name
        data_scope = Construct(scope, f"lookup-scope-{vpc_name}-{env}")
        vpc_lookup = DataGoogleComputeNetwork(
            data_scope,
            f"data-{vpc_name}-{env}",
            name=vpc_name,
            project=project_id
        )

        if vpc_name in vpc_modules:
            vpc_lookup.add_override("depends_on", [f"module.{vpc_modules[vpc_name].node.id}"])

        nat_module = nat_router(
            scope,
            f"{vpc_name}-nat-{env}",
            project_id=project_id,
            environment=env,
            subnet_ids_to_nat=nat_cfg["subnet_ids_to_nat"],
            vpc_id=vpc_lookup.self_link
        )

        nat_module.add_override("region", nat_cfg["region"])
        nat_module.add_override("num_nat_ips", nat_cfg.get("num_nat_ips", 1))

        nat_modules[env] = nat_module
        all_modules[env] = nat_module

    return nat_modules, all_modules