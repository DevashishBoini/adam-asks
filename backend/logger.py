"""
Logger setup for backend API
"""

import logging
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "backend_api.log")

# Clean the log file on server start
with open(LOG_FILE, "a") as f:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("backend_api")
