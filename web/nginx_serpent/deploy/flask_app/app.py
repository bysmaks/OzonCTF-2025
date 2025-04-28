# Add to imports at the top
from routes import app, start_maintenance_timer
from database import init_db, init_db_pool, execute_query, perform_maintenance
from docker_utils import client, shutdown_thread_pool
import docker
import signal
import sys
import atexit
import os
import logging
# Import for resource monitoring and cleanup management
import resource_monitor
import cleanup_manager

# Setup logging
logger = logging.getLogger('ctf-deployer')

# Initialize Docker client
client = docker.from_env()

# Global maintenance thread reference
maintenance_thread = None

# Function to cleanup all resources
def cleanup_all_resources():
    logger.info("Starting graceful shutdown and cleanup...")
    
    # First clean up all containers
    cleanup_all_containers()
    
    # Then shutdown the thread pool
    try:
        shutdown_thread_pool()
        logger.info("Thread pool shutdown complete")
    except Exception as e:
        logger.error(f"Error shutting down thread pool: {e}")
    
    # Shutdown cleanup manager
    try:
        cleanup_manager.shutdown()
        logger.info("Cleanup manager shutdown complete")
    except Exception as e:
        logger.error(f"Error shutting down cleanup manager: {e}")
    
    # Perform final database maintenance
    try:
        perform_maintenance()
        logger.info("Final database maintenance complete")
    except Exception as e:
        logger.error(f"Error during final maintenance: {e}")
    
    # Shutdown resource monitor
    try:
        resource_monitor.shutdown()
        logger.info("Resource monitor shutdown complete")
    except Exception as e:
        logger.error(f"Error shutting down resource monitor: {e}")
    
    logger.info("Cleanup complete. Exiting...")


# Function to cleanup all user containers
def cleanup_all_containers():
    logger.info("Cleaning up all user containers...")
    try:
        # Get all container IDs from the database
        containers = execute_query("SELECT id, port FROM containers")
        
        # Remove each container
        for container_data in containers:
            try:
                container_id = container_data[0]
                port = container_data[1]
                
                # Remove from Docker
                try:
                    container = client.containers.get(container_id)
                    container.remove(force=True)
                    logger.info(f"Removed container {container_id}")
                except docker.errors.NotFound:
                    logger.warning(f"Container {container_id} not found in Docker")
                except Exception as container_error:
                    logger.error(f"Error removing container {container_id}: {container_error}")
                
                # Release port in the database
                try:
                    from database import release_port
                    release_port(port)
                except Exception as port_error:
                    logger.error(f"Error releasing port {port}: {port_error}")
                
            except Exception as e:
                logger.error(f"Failed to process container cleanup for {container_data}: {e}")
        
        # Clear the database
        execute_query("DELETE FROM containers")
        logger.info("All containers cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# Register the cleanup function to run on exit
atexit.register(cleanup_all_resources)

# Handle SIGTERM and SIGINT properly
def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, initiating graceful shutdown...")
    cleanup_all_resources()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    # Initialize the database connection pool
    init_db_pool()
    
    # Initialize the database schema
    init_db()
    
    # Run initial maintenance to clean up any stale resources from previous runs
    try:
        logger.info("Running initial maintenance...")
        perform_maintenance()
        logger.info("Initial maintenance complete")
    except Exception as e:
        logger.error(f"Error during initial maintenance: {e}")
    
    # Initialize resource monitor
    try:
        logger.info("Initializing resource monitor...")
        resource_monitor.initialize()
        logger.info("Resource monitor initialized")
    except Exception as e:
        logger.error(f"Error initializing resource monitor: {e}")
    
    # Initialize the centralized cleanup manager
    try:
        logger.info("Initializing centralized cleanup manager...")
        cleanup_manager.initialize(client)
        logger.info("Cleanup manager initialized")
    except Exception as e:
        logger.error(f"Error initializing cleanup manager: {e}")
    
    # Start the maintenance timer for other maintenance tasks
    # The container cleanup is now handled by cleanup_manager
    maintenance_thread = start_maintenance_timer()
    
    # Get debug mode from environment variable
    debug_mode = os.environ.get('DEBUG_MODE', '').lower() == 'true'
    
    # Debug mode disables the reloader to avoid duplicate processes
    use_reloader = False if debug_mode else False
    
    # Start the Flask application
    logger.info(f"Starting Flask application (debug={debug_mode}, reloader={use_reloader})")
    app.run(host="0.0.0.0", port=5000, debug=debug_mode, use_reloader=use_reloader)
