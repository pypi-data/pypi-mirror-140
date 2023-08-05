
__all__ = ['CONFIG', 'DB_HOSTS', 'BASE_URL', 'API_BASE_URL']

import toml
import logging

# Read local `config.toml` file.
CONFIG = toml.load("/secrets/config.toml")
BASE_URL = "https://www.oddsportal.com"
API_BASE_URL = "https://fb.oddsportal.com"
# defined database hosts
DB_HOSTS = set([db for db in CONFIG["databases"]])

# config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
