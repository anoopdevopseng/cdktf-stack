from constructs import Construct
from cdktf import TerraformStack, TerraformModule, TerraformOutput
from cdktf_cdktf_provider_google.provider import GoogleProvider


class VpcStack(TerraformStack):
    def __init__(self, scope: Construct, id: str, project_id: str, region: str, vpc_list: list):
        super().__init__(scope, id)

        # Configure Google Provider
        GoogleProvider(self, "google", project=project_id, region=region)

        # Create VPCs
        self.vpc_outputs = {}
        self.all_modules = {}

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
                self,
                f"vpc-{vpc_name}",
                source="terraform-google-vpc",
            )

            vpc_module.add_override("project_id", project_id)
            vpc_module.add_override("name", vpc_name)
            vpc_module.add_override("routing_mode", vpc_cfg.get("routing_mode", "REGIONAL"))
            vpc_module.add_override("subnets", subnets_input)

            self.vpc_outputs[vpc_name] = vpc_module
            self.all_modules[vpc_name] = vpc_module

        # Create outputs for each VPC matching the original module structure
        for vpc_name, vpc_module in self.vpc_outputs.items():
            # VPC output - matches original "vpc" output
            TerraformOutput(
                self,
                f"{vpc_name}_vpc",
                value=vpc_module.get_string("vpc"),
                description=f"The created VPC network for {vpc_name}"
            )
            
            # Subnets output - matches original "subnets" output
            TerraformOutput(
                self,
                f"{vpc_name}_subnets",
                value=vpc_module.get_string("subnets"),
                description=f"The created subnets for the VPC network {vpc_name}"
            ) 