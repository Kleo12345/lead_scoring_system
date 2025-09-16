# lead_scoring_system/src/utils/config_loader.py
import yaml
from typing import Dict, Any
import os

def load_config(path: str = "/home/john/dev/python/snow_tools/lead_scoring_system/config/scoring_weights.yaml") -> Dict[str, Any]:
    """
    Load a YAML configuration file and return its contents as a dictionary.
    
    The supplied `path` is resolved relative to the repository root (three levels above this file).
    If `path` is absolute, that absolute path will be used.
    
    Parameters:
        path (str): Filesystem path to the YAML configuration file. Defaults to
            "/home/john/dev/python/snow_tools/lead_scoring_system/config/scoring_weights.yaml".
    
    Returns:
        Dict[str, Any]: Parsed contents of the YAML file.
    
    Raises:
        FileNotFoundError: If the resolved configuration file does not exist.
    """
    # Navigate up to the project root to find the config file
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(project_root, path)
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)