"""
Prometheus metrics definitions for the CTF Deployer.
This module defines all metrics that will be exposed to Prometheus.
"""
import time
import logging
from prometheus_client import Counter, Gauge, Histogram, Summary, Info

# Setup logging
logger = logging.getLogger('ctf-deployer')

# Define metrics with appropriate labels
# System information
INFO = Info('ctf_deployer', 'Information about the CTF Deployer instance')

# Resource usage metrics
RESOURCE_USAGE = Gauge('ctf_resource_usage_percent', 
                       'Current resource usage as percentage of limit',
                       ['resource_type'])

RESOURCE_CURRENT = Gauge('ctf_resource_current', 
                        'Current resource usage in absolute units',
                        ['resource_type', 'unit'])

RESOURCE_LIMIT = Gauge('ctf_resource_limit', 
                      'Resource usage limit in absolute units',
                      ['resource_type', 'unit'])

# Container metrics
ACTIVE_CONTAINERS = Gauge('ctf_active_containers', 
                         'Number of currently active challenge containers')

CONTAINER_DEPLOYMENTS_TOTAL = Counter('ctf_container_deployments_total', 
                                    'Total number of container deployments')

CONTAINER_DEPLOYMENT_DURATION = Histogram('ctf_container_deployment_duration_seconds', 
                                        'Time taken to deploy a container',
                                        buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0])

CONTAINER_LIFETIME = Histogram('ctf_container_lifetime_seconds', 
                              'Lifetime of containers',
                              buckets=[60, 300, 600, 1800, 3600, 7200, 14400, 28800])

# Rate limiting metrics
RATE_LIMIT_CHECKS = Counter('ctf_rate_limit_checks_total', 
                           'Total number of rate limit checks')

RATE_LIMIT_REJECTIONS = Counter('ctf_rate_limit_rejections_total', 
                               'Total number of rejected requests due to rate limiting')

# Resource quota metrics
RESOURCE_QUOTA_CHECKS = Counter('ctf_resource_quota_checks_total', 
                               'Total number of resource quota checks')

RESOURCE_QUOTA_REJECTIONS = Counter('ctf_resource_quota_rejections_total', 
                                   'Total number of rejected requests due to resource quotas',
                                   ['resource_type'])

# Captcha metrics
CAPTCHA_GENERATED = Counter('ctf_captcha_generated_total', 
                           'Total number of captchas generated')

CAPTCHA_VALIDATIONS = Counter('ctf_captcha_validations_total', 
                             'Total number of captcha validations')

# Container action metrics
CONTAINER_RESTARTS = Counter('ctf_container_restarts_total', 
                            'Total number of container restarts')

CONTAINER_LIFETIME_EXTENSIONS = Counter('ctf_container_lifetime_extensions_total', 
                                      'Total number of container lifetime extensions')

# Error metrics
ERRORS_TOTAL = Counter('ctf_errors_total', 
                      'Total number of errors',
                      ['error_type'])

# Database metrics
DB_OPERATIONS = Counter('ctf_database_operations_total', 
                       'Total number of database operations',
                       ['operation_type'])

DB_OPERATION_DURATION = Histogram('ctf_database_operation_duration_seconds', 
                                'Time taken for database operations',
                                ['operation_type'],
                                buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0])

DB_CONNECTION_POOL = Gauge('ctf_database_connection_pool', 
                          'Database connection pool statistics',
                          ['state'])

# Port allocation metrics
PORT_POOL = Gauge('ctf_port_pool', 
                 'Port pool statistics',
                 ['state'])

PORT_ALLOCATION_FAILURES = Counter('ctf_port_allocation_failures_total', 
                                  'Total number of port allocation failures')

def initialize_metrics(deployer_info):
    """Initialize metrics with static information"""
    try:
        # Set system information
        INFO.info({
            'version': deployer_info.get('version', 'unknown'),
            'challenge': deployer_info.get('challenge_title', 'unknown'),
            'hostname': deployer_info.get('hostname', 'unknown'),
            'start_time': str(int(time.time()))
        })
        
        # Set resource limits (these don't change)
        RESOURCE_LIMIT.labels('containers', 'count').set(deployer_info.get('max_containers', 0))
        RESOURCE_LIMIT.labels('cpu', 'percent').set(deployer_info.get('max_cpu_percent', 0))
        RESOURCE_LIMIT.labels('memory', 'gb').set(deployer_info.get('max_memory_gb', 0))
        
        logger.info("Prometheus metrics initialized")
    except Exception as e:
        logger.error(f"Failed to initialize metrics: {str(e)}")

def update_resource_metrics(resource_usage):
    """Update resource metrics with current usage"""
    try:
        # Update resource percentages
        RESOURCE_USAGE.labels('containers').set(resource_usage['containers']['percent'])
        RESOURCE_USAGE.labels('cpu').set(resource_usage['cpu']['percent'])
        RESOURCE_USAGE.labels('memory').set(resource_usage['memory']['percent'])
        
        # Update current values
        RESOURCE_CURRENT.labels('containers', 'count').set(resource_usage['containers']['current'])
        RESOURCE_CURRENT.labels('cpu', 'percent').set(resource_usage['cpu']['current'])
        RESOURCE_CURRENT.labels('memory', 'gb').set(resource_usage['memory']['current'])
        
        # Update active containers gauge
        ACTIVE_CONTAINERS.set(resource_usage['containers']['current'])
    except Exception as e:
        logger.error(f"Failed to update resource metrics: {str(e)}")

def update_port_pool_metrics(total_ports, allocated_ports):
    """Update port pool metrics"""
    try:
        PORT_POOL.labels('total').set(total_ports)
        PORT_POOL.labels('allocated').set(allocated_ports)
        PORT_POOL.labels('available').set(total_ports - allocated_ports)
    except Exception as e:
        logger.error(f"Failed to update port pool metrics: {str(e)}")

def update_db_connection_metrics(pool_stats):
    """Update database connection pool metrics"""
    try:
        # Use only the metrics that we know we can reliably get
        
        # Min connections
        if isinstance(pool_stats.get('min_connections'), (int, float)):
            DB_CONNECTION_POOL.labels('min').set(pool_stats.get('min_connections', 0))
            
        # Max connections
        if isinstance(pool_stats.get('max_connections'), (int, float)):
            DB_CONNECTION_POOL.labels('max').set(pool_stats.get('max_connections', 0))
            
        # Set the status
        if pool_stats.get('status') == 'active':
            DB_CONNECTION_POOL.labels('status').set(1)
        else:
            DB_CONNECTION_POOL.labels('status').set(0)
            
    except Exception as e:
        logger.error(f"Failed to update database connection metrics: {str(e)}")

# Context manager for timing operations
class TimingContext:
    """Context manager for timing operations and recording metrics"""
    def __init__(self, metric, labels=None):
        self.metric = metric
        self.labels = labels or {}
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Record error
            ERRORS_TOTAL.labels(error_type=exc_type.__name__).inc()
        
        # Record duration
        if self.start_time is not None:
            duration = time.time() - self.start_time
            if isinstance(self.metric, Histogram) or isinstance(self.metric, Summary):
                if self.labels:
                    self.metric.labels(**self.labels).observe(duration)
                else:
                    self.metric.observe(duration)
