import os
from pathlib import Path
import yaml

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

def load_config(config_path=CONFIG_PATH):
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config

CONFIG = load_config()

# Absolute paths to avoid any hardcoded issues
PREPROCESSOR_PATH = BASE_DIR / CONFIG["paths"]["preprocessor_path"]
MODEL_PATH = BASE_DIR / CONFIG["paths"]["model_path"]
LOGS_DIR = BASE_DIR / CONFIG["paths"]["logs_dir"]

os.makedirs(LOGS_DIR, exist_ok=True)