import yaml
import logging.config

def setup_logging():
    with open("config/logging.yaml", "r") as f:
        logging_config = yaml.safe_load(f)
        logging.config.dictConfig(logging_config)