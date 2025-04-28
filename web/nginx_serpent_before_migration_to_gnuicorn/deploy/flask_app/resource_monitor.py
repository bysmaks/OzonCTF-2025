import threading
import time
import logging
import docker
import json
import os
import sys
from collections import defaultdict
from config import (
    MAX_TOTAL_CONTAINERS, MAX_TOTAL_CPU_PERCENT, MAX_TOTAL_MEMORY_GB,
    RESOURCE_CHECK_INTERVAL, RESOURCE_SOFT_LIMIT_PERCENT, ENABLE_RESOURCE_QUOTAS,
    CHALLENGE_TITLE
)
from database import execute_query
import metrics

# Setup logging
logger = logging.getLogger('ctf-deployer')

# Try to import psutil for system monitoring, but continue if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
    logger.info("psutil library available - system-level monitoring enabled")
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil library not available - system-level monitoring disabled")

# Global resource usage tracker
resource_usage = {
    "containers": {
        "current": 0,
        "limit": MAX_TOTAL_CONTAINERS,
        "percent": 0
    },
    "cpu": {
        "current": 0,  # In percentage points (100% = 1 core)
        "limit": MAX_TOTAL_CPU_PERCENT,
        "percent": 0
    },
    "memory": {
        "current": 0,  # In GB
        "limit": MAX_TOTAL_MEMORY_GB,
        "percent": 0
    },
    "last_updated": 0,
    "status": "initializing"
}

# Lock for thread safety when updating resource usage
resource_lock = threading.RLock()

# Reference to monitoring thread
monitor_thread = None

# Docker client
docker_client = None

def initialize():
    """Initialize the resource monitor"""
    global docker_client
    
    try:
        # Initialize Docker client
        docker_client = docker.from_env()
        
        # Initialize Prometheus metrics
        deployer_info = {
            'version': '1.2',  # Version from README.md
            'challenge_title': CHALLENGE_TITLE,
            'hostname': os.uname().nodename,
            'max_containers': MAX_TOTAL_CONTAINERS,
            'max_cpu_percent': MAX_TOTAL_CPU_PERCENT,
            'max_memory_gb': MAX_TOTAL_MEMORY_GB
        }
        metrics.initialize_metrics(deployer_info)
        
        # Log initialization
        logger.info("Resource monitor initialized")
        
        # Create monitoring thread if resource quotas are enabled
        if ENABLE_RESOURCE_QUOTAS:
            start_monitoring()
        else:
            logger.info("Resource quotas disabled - monitoring not started")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize resource monitor: {str(e)}")
        return False

def start_monitoring():
    """Start the resource monitoring thread"""
    global monitor_thread
    
    if monitor_thread and monitor_thread.is_alive():
        logger.warning("Resource monitor thread already running")
        return
    
    try:
        # Create and start monitoring thread
        monitor_thread = threading.Thread(target=_monitoring_loop, daemon=True)
        monitor_thread.start()
        logger.info(f"Resource monitoring started with interval {RESOURCE_CHECK_INTERVAL}s")
        
        # Update status
        with resource_lock:
            resource_usage["status"] = "active"
    except Exception as e:
        logger.error(f"Failed to start resource monitoring thread: {str(e)}")
        resource_usage["status"] = "error"

def _monitoring_loop():
    """Background thread function to periodically update resource usage"""
    while True:
        try:
            update_resource_usage()
            time.sleep(RESOURCE_CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Error in resource monitoring loop: {str(e)}")
            time.sleep(RESOURCE_CHECK_INTERVAL * 2)  # Wait longer after error

def update_resource_usage():
    """Update current resource usage statistics"""
    if not ENABLE_RESOURCE_QUOTAS:
        return
        
    try:
        # Count active containers from database
        container_count = execute_query("SELECT COUNT(*) FROM containers", fetchone=True)[0]
        
        # Get Docker container stats
        cpu_percent_total = 0
        memory_gb_total = 0
        
        if docker_client:
            # Get all running containers
            containers = docker_client.containers.list()
            
            # Get stats for each container
            for container in containers:
                try:
                    # Get container stats
                    stats = container.stats(stream=False)
                    
                    # Extract CPU usage
                    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                    
                    if system_delta > 0:
                        cpu_percent = (cpu_delta / system_delta) * 100.0 * stats['cpu_stats']['online_cpus']
                        cpu_percent_total += cpu_percent
                    
                    # Extract memory usage
                    memory_usage = stats['memory_stats'].get('usage', 0)
                    if memory_usage:
                        memory_gb = memory_usage / (1024 * 1024 * 1024)  # Convert bytes to GB
                        memory_gb_total += memory_gb
                except Exception as e:
                    logger.warning(f"Failed to get stats for container {container.id}: {str(e)}")
        
        # Get system stats if psutil is available
        system_cpu_percent = 0
        system_memory_gb = 0
        
        if PSUTIL_AVAILABLE:
            system_cpu_percent = psutil.cpu_percent(interval=None) * psutil.cpu_count()
            system_memory_gb = psutil.virtual_memory().used / (1024 * 1024 * 1024)  # Convert bytes to GB
            
            # If Docker stats are much lower than system stats, use system stats
            # as they're likely more accurate (accounts for Docker daemon overhead)
            if system_cpu_percent > cpu_percent_total * 1.5:
                cpu_percent_total = system_cpu_percent
                
            if system_memory_gb > memory_gb_total * 1.5:
                memory_gb_total = system_memory_gb
        
        # Update resource usage with lock for thread safety
        with resource_lock:
            resource_usage["containers"]["current"] = container_count
            resource_usage["containers"]["percent"] = (container_count / MAX_TOTAL_CONTAINERS) * 100 if MAX_TOTAL_CONTAINERS > 0 else 0
            
            resource_usage["cpu"]["current"] = cpu_percent_total
            resource_usage["cpu"]["percent"] = (cpu_percent_total / MAX_TOTAL_CPU_PERCENT) * 100 if MAX_TOTAL_CPU_PERCENT > 0 else 0
            
            resource_usage["memory"]["current"] = memory_gb_total
            resource_usage["memory"]["percent"] = (memory_gb_total / MAX_TOTAL_MEMORY_GB) * 100 if MAX_TOTAL_MEMORY_GB > 0 else 0
            
            resource_usage["last_updated"] = int(time.time())
            resource_usage["status"] = "active"
        
        # Update Prometheus metrics
        metrics.update_resource_metrics(resource_usage)
        
        # Log current usage if it's getting high
        _log_high_usage()
        
        # Get and update port pool metrics
        try:
            total_ports = execute_query("SELECT COUNT(*) FROM port_allocations", fetchone=True)[0]
            allocated_ports = execute_query("SELECT COUNT(*) FROM port_allocations WHERE allocated = TRUE", fetchone=True)[0]
            metrics.update_port_pool_metrics(total_ports, allocated_ports)
        except Exception as e:
            logger.error(f"Failed to update port pool metrics: {str(e)}")
            
    except Exception as e:
        logger.error(f"Failed to update resource usage: {str(e)}")
        with resource_lock:
            resource_usage["status"] = "error"

def _log_high_usage():
    """Log warning if resource usage is high"""
    soft_limit = RESOURCE_SOFT_LIMIT_PERCENT
    
    # Check container count
    if resource_usage["containers"]["percent"] >= soft_limit:
        logger.warning(f"High container count: {resource_usage['containers']['current']}/{MAX_TOTAL_CONTAINERS} "
                      f"({resource_usage['containers']['percent']:.1f}%)")
    
    # Check CPU usage
    if resource_usage["cpu"]["percent"] >= soft_limit:
        logger.warning(f"High CPU usage: {resource_usage['cpu']['current']:.1f}%/{MAX_TOTAL_CPU_PERCENT}% "
                      f"({resource_usage['cpu']['percent']:.1f}%)")
    
    # Check memory usage
    if resource_usage["memory"]["percent"] >= soft_limit:
        logger.warning(f"High memory usage: {resource_usage['memory']['current']:.2f}GB/{MAX_TOTAL_MEMORY_GB}GB "
                      f"({resource_usage['memory']['percent']:.1f}%)")

def get_resource_usage():
    """Get current resource usage (thread-safe)"""
    with resource_lock:
        return dict(resource_usage)

def check_resource_availability(container_cpu=None, container_memory=None):
    """
    Check if resources are available for a new container
    
    Args:
        container_cpu: Expected CPU usage for the new container (in percent)
        container_memory: Expected memory usage for the new container (in GB)
        
    Returns:
        (bool, str): Tuple of (resources_available, message)
    """
    # Increment Prometheus counter for resource quota checks
    metrics.RESOURCE_QUOTA_CHECKS.inc()
    
    if not ENABLE_RESOURCE_QUOTAS:
        return True, "Resource quotas disabled"
        
    # Set default resource expectations if not provided
    if container_cpu is None:
        container_cpu = 100  # Assume 100% of one core
        
    if container_memory is None:
        container_memory = 0.5  # Assume 500MB
        
    # Get current usage
    usage = get_resource_usage()
    
    # Force usage update if it's too old
    if usage["last_updated"] < int(time.time()) - (RESOURCE_CHECK_INTERVAL * 3):
        update_resource_usage()
        usage = get_resource_usage()
    
    # Check container count
    if usage["containers"]["current"] >= MAX_TOTAL_CONTAINERS:
        metrics.RESOURCE_QUOTA_REJECTIONS.labels(resource_type='containers').inc()
        return False, f"Maximum number of containers reached ({MAX_TOTAL_CONTAINERS})"
    
    # Check CPU usage
    expected_cpu = usage["cpu"]["current"] + container_cpu
    if expected_cpu > MAX_TOTAL_CPU_PERCENT:
        metrics.RESOURCE_QUOTA_REJECTIONS.labels(resource_type='cpu').inc()
        return False, f"CPU usage limit reached ({usage['cpu']['current']:.1f}%/{MAX_TOTAL_CPU_PERCENT}%)"
    
    # Check memory usage
    expected_memory = usage["memory"]["current"] + container_memory
    if expected_memory > MAX_TOTAL_MEMORY_GB:
        metrics.RESOURCE_QUOTA_REJECTIONS.labels(resource_type='memory').inc()
        return False, f"Memory usage limit reached ({usage['memory']['current']:.2f}GB/{MAX_TOTAL_MEMORY_GB}GB)"
    
    return True, "Resources available"

def shutdown():
    """Shutdown the resource monitor"""
    global monitor_thread
    
    logger.info("Shutting down resource monitor")
    
    # Thread will terminate automatically as it's a daemon thread
    monitor_thread = None
    
    with resource_lock:
        resource_usage["status"] = "shutdown"
