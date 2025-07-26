# CDKTF Stack v2

This project uses CDK for Terraform (CDKTF) to manage Google Cloud Platform infrastructure with a modular stack approach.

## Architecture

The infrastructure is organized into three separate stacks:

1. **VPC Stack** (`stacks/vpc_stack.py`) - Manages Virtual Private Clouds and subnets
2. **NAT Stack** (`stacks/nat_stack.py`) - Manages Cloud NAT gateways
3. **GKE Stack** (`stacks/gke_stack.py`) - Manages Google Kubernetes Engine clusters

## Prerequisites

- Python 3.8+
- CDKTF CLI
- Google Cloud SDK
- Terraform

## Installation

1. Install dependencies:
```bash
pipenv install
```

2. Install CDKTF:
```bash
npm install -g cdktf-cli
```

## Usage

### Running the Stacks

1. Set the environment variable:
```bash
# For development
ENV=dev python main.py

# For pre-production
ENV=preprod python main.py

# For production
ENV=prod python main.py
```

2. Deploy the stacks:
```bash
# Deploy all stacks in a single command (recommended)
cdktf deploy --all

# OR deploy individual stacks (if needed)
# Deploy VPC stack first
cdktf deploy vpc-stack-dev

# Deploy NAT stack (depends on VPC)
cdktf deploy nat-stack-dev

# Deploy GKE stack (depends on VPC and NAT)
cdktf deploy gke-stack-dev
```

### Testing

Run the test script to verify the stack structure:
```bash
python test_stacks.py
```

## Stack Outputs

Each stack provides outputs that can be referenced by other stacks or external systems.

### VPC Stack Outputs

For each VPC, the following outputs are available (matching the original VPC module):
- `{vpc_name}_vpc` - The created VPC network object
- `{vpc_name}_subnets` - The created subnets object

### NAT Stack Outputs

For each NAT gateway, the following outputs are available (matching the original NAT module):
- `nat_ips_{env}` - The created NAT IPs

### GKE Stack Outputs

For each GKE cluster, the following outputs are available (matching the original GKE module):
- `{cluster_name}_name` - Cluster name
- `{cluster_name}_location` - Cluster location
- `{cluster_name}_endpoint` - Cluster endpoint
- `{cluster_name}_master_auth` - Master authentication (sensitive)
- `{cluster_name}_node_pool` - Node pool information

## Configuration

Configuration is managed through YAML files in the `envs/` directory:

- `envs/dev.yaml` - Development environment
- `envs/preprod.yaml` - Pre-production environment
- `envs/prod.yaml` - Production environment

## Stack Dependencies

The stacks have the following dependency order:
1. VPC Stack (no dependencies)
2. NAT Stack (depends on VPC Stack)
3. GKE Stack (depends on VPC and NAT Stacks)

### Automatic Dependency Resolution

When using `cdktf deploy --all`, CDKTF automatically:
- Detects dependencies between stacks
- Deploys stacks in the correct order
- Handles cross-stack references
- Ensures all dependencies are satisfied before deploying dependent stacks

This means you can safely run `cdktf deploy --all` and CDKTF will handle the deployment order automatically.

## Changes from Previous Version

- Converted functions to proper CDKTF stacks
- Removed ArgoCD functionality
- Added comprehensive outputs to each stack
- Improved stack dependency management
- Enhanced error handling and logging
- Centralized module source configuration in `cdktf.json`
- Moved hardcoded module URLs to configuration files

## Troubleshooting

### Common Issues

1. **Module not found errors**: Ensure all dependencies are installed
2. **Provider configuration errors**: Verify Google Cloud credentials
3. **Stack dependency errors**: Deploy stacks in the correct order

### Getting Help

For issues or questions, please check the CDKTF documentation or create an issue in the repository.