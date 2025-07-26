from constructs import Construct
from cdktf import TerraformStack, TerraformModule, TerraformOutput
from cdktf_cdktf_provider_google.provider import GoogleProvider
from cdktf_cdktf_provider_google.data_google_compute_network import DataGoogleComputeNetwork


class NatStack(TerraformStack):
    def __init__(self, scope: Construct, id: str, project_id: str, region: str, nat_list: list, vpc_modules: dict):
        super().__init__(scope, id)

        # Configure Google Provider
        GoogleProvider(self, "google", project=project_id, region=region)

        # Create NATs
        self.nat_modules = {}
        self.all_modules = {}

        for nat_cfg in nat_list:
            env = nat_cfg["environment"]
            vpc_name = nat_cfg["vpc_id"]

            depends_on = []
            
            # Lookup VPC self_link by name
            data_scope = Construct(self, f"lookup-scope-{vpc_name}-{env}")
            vpc_lookup = DataGoogleComputeNetwork(
                data_scope,
                f"data-{vpc_name}-{env}",
                name=vpc_name,
                project=project_id
            )

            if vpc_name in vpc_modules:
                vpc_lookup.add_override("depends_on", [f"module.{vpc_modules[vpc_name].node.id}"])

            nat_module = TerraformModule(
                self,
                f"{vpc_name}-nat-{env}",
                source="terraform-google-cloudnat"
            )

            nat_module.add_override("project_id", project_id)
            nat_module.add_override("environment", env)
            nat_module.add_override("region", nat_cfg["region"])
            nat_module.add_override("vpc_id", vpc_lookup.self_link)
            nat_module.add_override("num_nat_ips", nat_cfg.get("num_nat_ips", 1))
            nat_module.add_override("subnet_ids_to_nat", nat_cfg["subnet_ids_to_nat"])

            self.nat_modules[env] = nat_module
            self.all_modules[env] = nat_module

        # Create outputs for each NAT matching the original module structure
        for env, nat_module in self.nat_modules.items():
            # NAT IPs output - matches original "nat_ips" output
            TerraformOutput(
                self,
                f"nat_ips_{env}",
                value=nat_module.get_string("nat_ips"),
                description=f"The created NAT IPs for environment {env}"
            ) 