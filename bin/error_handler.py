import logging
import sys

import os

# Ensure logs directory exists
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'atlas_core.log')

logging.basicConfig(filename=LOG_FILE, level=logging.ERROR)

def safe_execute(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logging.error(f'Critical failure in {func.__name__}: {str(e)}', exc_info=True)
        # Graceful degradation: return None or neutral state instead of crashing
        return None

def monitor_resources():
    import psutil
    mem = psutil.virtual_memory().percent
    if mem > 95:
        sys.exit(0) # Emergency exit for Celeron hardware safety
