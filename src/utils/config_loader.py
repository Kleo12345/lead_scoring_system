# lead_scoring_system/src/utils/config_loader.py
import yaml
from typing import Dict, Any
import os

def load_config(path: str = "/home/john/dev/python/snow_tools/lead_scoring_system/config/scoring_weights.yaml") -> Dict[str, Any]:
    """
    Loads the YAML configuration file from the project's root directory.
    """
    # Navigate up to the project root to find the config file
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(project_root, path)
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)