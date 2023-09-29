from dataclasses import dataclass, fields, asdict
import configparser

import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

def _read_config_to_dict(config: configparser.ConfigParser) -> dict:
    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for key, val in config.items(section):
            config_dict[section][key] = val  # You can convert val to int, float, etc. as needed
    return config_dict 


def read_config(current_dir: str) -> dict:    
    # Define settings file path
    config_file_path = os.path.join(current_dir, 'config', 'settings.ini')
    # Read configuration file
    config = configparser.ConfigParser()
    config.read(config_file_path)
    logger.info(f'Read configuration file: {config_file_path}')
    return _read_config_to_dict(config)
    
    