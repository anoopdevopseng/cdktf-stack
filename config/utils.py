import yaml
import os

def load_config(yaml_path: str) -> dict:
    """
    Load configuration from a YAML file.
    
    Args:
        yaml_path (str): Path to the YAML configuration file
        
    Returns:
        dict: Configuration dictionary
        
    Raises:
        FileNotFoundError: If the YAML file doesn't exist
        yaml.YAMLError: If the YAML file is malformed
    """
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Configuration file not found: {yaml_path}")
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file {yaml_path}: {e}")
    except Exception as e:
        raise Exception(f"Error loading configuration from {yaml_path}: {e}") 