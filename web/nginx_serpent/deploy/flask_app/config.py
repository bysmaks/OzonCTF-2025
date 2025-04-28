import os
import sys
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ctf-deployer')

# Try multiple possible locations for .env file
possible_paths = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'),
    "/app/.env",        # Common Docker container mount location
    "/.env",            # Root location
    "./.env",           # Current directory
    os.path.abspath('.env')  # Absolute path to current directory .env
]

env_loaded = False
for env_path in possible_paths:
    if os.path.exists(env_path):
        logger.info(f"Found .env file at: {env_path}")
        if load_dotenv(env_path):
            logger.info(f"Successfully loaded environment from {env_path}")
            env_loaded = True
            break
        else:
            logger.warning(f"Found but failed to load .env from {env_path}")

if not env_loaded:
    logger.error("Failed to load environment file. Checked paths:")
    for path in possible_paths:
        logger.error(f"  - {path}")
    logger.error("Cannot continue without environment variables")
    sys.exit(1)

# Helper function to get required environment variables with no default
def get_env_or_fail(var_name, convert_func=str):
    """Get environment variable, fail if not set"""
    value = os.getenv(var_name)
    if value is None:
        logger.error(f"Required environment variable {var_name} is not set")
        sys.exit(1)
    try:
        return convert_func(value)
    except Exception as e:
        logger.error(f"Failed to convert {var_name} value '{value}': {str(e)}")
        sys.exit(1)

# Container identification and time settings
COMPOSE_PROJECT_NAME = get_env_or_fail('COMPOSE_PROJECT_NAME')
LEAVE_TIME = get_env_or_fail('LEAVE_TIME', int)
ADD_TIME = get_env_or_fail('ADD_TIME', int)
IMAGES_NAME = get_env_or_fail('IMAGES_NAME')
FLAG = get_env_or_fail('FLAG')

# Port configuration
PORT_IN_CONTAINER = get_env_or_fail('PORT_IN_CONTAINER', int)
START_RANGE = get_env_or_fail('START_RANGE', int)
STOP_RANGE = get_env_or_fail('STOP_RANGE', int)
FLASK_APP_PORT = get_env_or_fail('FLASK_APP_PORT', int)
DIRECT_TEST_PORT = get_env_or_fail('DIRECT_TEST_PORT', int)

# Network configuration
NETWORK_NAME = get_env_or_fail('NETWORK_NAME')
NETWORK_SUBNET = get_env_or_fail('NETWORK_SUBNET')

# Database settings
DB_HOST = get_env_or_fail('DB_HOST')
DB_PORT = get_env_or_fail('DB_PORT', int)
DB_NAME = get_env_or_fail('DB_NAME')
DB_USER = get_env_or_fail('DB_USER')
DB_PASSWORD = get_env_or_fail('DB_PASSWORD')
DB_POOL_MIN = get_env_or_fail('DB_POOL_MIN', int)
DB_POOL_MAX = get_env_or_fail('DB_POOL_MAX', int)

# Challenge details
CHALLENGE_TITLE = get_env_or_fail('CHALLENGE_TITLE')
CHALLENGE_DESCRIPTION = get_env_or_fail('CHALLENGE_DESCRIPTION')
COMMAND_CONNECT = get_env_or_fail('COMMAND_CONNECT')

# Resource limits for user containers
CONTAINER_MEMORY_LIMIT = get_env_or_fail('CONTAINER_MEMORY_LIMIT')
CONTAINER_SWAP_LIMIT = get_env_or_fail('CONTAINER_SWAP_LIMIT')
CONTAINER_CPU_LIMIT = get_env_or_fail('CONTAINER_CPU_LIMIT', float)
CONTAINER_PIDS_LIMIT = get_env_or_fail('CONTAINER_PIDS_LIMIT', int)

# Security options for user containers
ENABLE_NO_NEW_PRIVILEGES = get_env_or_fail('ENABLE_NO_NEW_PRIVILEGES', lambda x: x.lower() == 'true')
ENABLE_READ_ONLY = get_env_or_fail('ENABLE_READ_ONLY', lambda x: x.lower() == 'true')
ENABLE_TMPFS = get_env_or_fail('ENABLE_TMPFS', lambda x: x.lower() == 'true')
TMPFS_SIZE = get_env_or_fail('TMPFS_SIZE')

# Container capability configuration
DROP_ALL_CAPABILITIES = get_env_or_fail('DROP_ALL_CAPABILITIES', lambda x: x.lower() == 'true')
CAP_NET_BIND_SERVICE = get_env_or_fail('CAP_NET_BIND_SERVICE', lambda x: x.lower() == 'true')
CAP_CHOWN = get_env_or_fail('CAP_CHOWN', lambda x: x.lower() == 'true')

# Rate limiting to prevent abuse
MAX_CONTAINERS_PER_HOUR = get_env_or_fail('MAX_CONTAINERS_PER_HOUR', int)
RATE_LIMIT_WINDOW = get_env_or_fail('RATE_LIMIT_WINDOW', int)

# Testing/Debugging settings
DEBUG_MODE = get_env_or_fail('DEBUG_MODE', lambda x: x.lower() == 'true')
BYPASS_CAPTCHA = get_env_or_fail('BYPASS_CAPTCHA', lambda x: x.lower() == 'true')

# Thread pool configuration
THREAD_POOL_SIZE = get_env_or_fail('THREAD_POOL_SIZE', int)
MAINTENANCE_INTERVAL = get_env_or_fail('MAINTENANCE_INTERVAL', int)
CONTAINER_CHECK_INTERVAL = get_env_or_fail('CONTAINER_CHECK_INTERVAL', int)
CAPTCHA_TTL = get_env_or_fail('CAPTCHA_TTL', int)

# Resource allocation settings
PORT_ALLOCATION_MAX_ATTEMPTS = get_env_or_fail('PORT_ALLOCATION_MAX_ATTEMPTS', int)
STALE_PORT_MAX_AGE = get_env_or_fail('STALE_PORT_MAX_AGE', int)

# Maintenance cleanup settings
MAINTENANCE_BATCH_SIZE = get_env_or_fail('MAINTENANCE_BATCH_SIZE', int)
MAINTENANCE_POOL_MIN = get_env_or_fail('MAINTENANCE_POOL_MIN', int)
MAINTENANCE_POOL_MAX = get_env_or_fail('MAINTENANCE_POOL_MAX', int)

# Global resource quotas
MAX_TOTAL_CONTAINERS = get_env_or_fail('MAX_TOTAL_CONTAINERS', int)
MAX_TOTAL_CPU_PERCENT = get_env_or_fail('MAX_TOTAL_CPU_PERCENT', int)
MAX_TOTAL_MEMORY_GB = get_env_or_fail('MAX_TOTAL_MEMORY_GB', float)
RESOURCE_CHECK_INTERVAL = get_env_or_fail('RESOURCE_CHECK_INTERVAL', int)
RESOURCE_SOFT_LIMIT_PERCENT = get_env_or_fail('RESOURCE_SOFT_LIMIT_PERCENT', int)
ENABLE_RESOURCE_QUOTAS = get_env_or_fail('ENABLE_RESOURCE_QUOTAS', lambda x: x.lower() == 'true')

# Metrics configuration
METRICS_ENABLED = get_env_or_fail('METRICS_ENABLED', lambda x: x.lower() == 'true')
ENABLE_LOGS_ENDPOINT = get_env_or_fail('ENABLE_LOGS_ENDPOINT', lambda x: x.lower() == 'true')
ADMIN_KEY = get_env_or_fail('ADMIN_KEY')

# Validation checks
if START_RANGE >= STOP_RANGE:
    logger.error(f"START_RANGE ({START_RANGE}) must be less than STOP_RANGE ({STOP_RANGE})")
    sys.exit(1)

if LEAVE_TIME <= 0 or ADD_TIME <= 0:
    logger.error(f"LEAVE_TIME ({LEAVE_TIME}) and ADD_TIME ({ADD_TIME}) must be positive")
    sys.exit(1)

logger.info("Configuration loaded successfully")
