"""
Centralized container cleanup manager for CTF Deployer.
Provides batch processing of expired containers instead of individual monitoring threads.
"""
import time
import threading
import logging
import docker
from datetime import datetime
import psycopg2
from config import (
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD,
    MAINTENANCE_INTERVAL, MAINTENANCE_BATCH_SIZE, 
    MAINTENANCE_POOL_MIN, MAINTENANCE_POOL_MAX
)

# Setup logging
logger = logging.getLogger('ctf-deployer')

# Global variables
cleanup_thread = None
stop_signal = threading.Event()
docker_client = None
maintenance_pool = None  # Dedicated connection pool just for cleanup operations

def initialize(client):
    """Initialize the cleanup manager with configuration from environment variables.
    
    Args:
        client: Docker client instance
    """
    global docker_client, maintenance_pool, cleanup_thread, stop_signal
    
    # Store the Docker client
    docker_client = client
    
    # Initialize dedicated connection pool for maintenance
    try:
        from psycopg2 import pool
        maintenance_pool = pool.ThreadedConnectionPool(
            MAINTENANCE_POOL_MIN,
            MAINTENANCE_POOL_MAX,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info(f"Initialized dedicated maintenance connection pool with {MAINTENANCE_POOL_MIN}-{MAINTENANCE_POOL_MAX} connections")
    except Exception as e:
        logger.error(f"Failed to initialize maintenance connection pool: {str(e)}")
        # Fall back to using the main pool if dedicated pool fails
        maintenance_pool = None
    
    # Reset stop signal
    stop_signal.clear()
    
    # Start the cleanup thread if not already running
    if cleanup_thread is None or not cleanup_thread.is_alive():
        cleanup_thread = threading.Thread(
            target=cleanup_loop,
            args=(MAINTENANCE_INTERVAL, MAINTENANCE_BATCH_SIZE),
            daemon=True
        )
        cleanup_thread.start()
        logger.info(f"Started centralized container cleanup thread with {MAINTENANCE_INTERVAL}s interval and batch size {MAINTENANCE_BATCH_SIZE}")
    
    return True

def get_maintenance_connection():
    """Get a database connection from the maintenance pool or fall back to the main pool."""
    if maintenance_pool is not None:
        try:
            return maintenance_pool.getconn()
        except Exception as e:
            logger.error(f"Error getting connection from maintenance pool: {str(e)}")
    
    # Fall back to main connection pool
    from database import get_connection
    return get_connection()

def release_maintenance_connection(conn):
    """Release a connection back to the maintenance pool."""
    if conn is None:
        return
        
    if maintenance_pool is not None:
        try:
            maintenance_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error releasing connection to maintenance pool: {str(e)}")
    else:
        # Fall back to main connection pool
        from database import release_connection
        release_connection(conn)

def cleanup_loop(check_interval, batch_size):
    """Main cleanup loop that runs continuously checking for expired containers."""
    logger.info("Starting centralized container cleanup loop")
    
    while not stop_signal.is_set():
        try:
            # Process expired containers in batches
            process_expired_containers(batch_size)
            
            # Wait for the next check interval or until stop signal
            stop_signal.wait(timeout=check_interval)
        except Exception as e:
            logger.error(f"Error in cleanup loop: {str(e)}")
            # Wait a bit before retrying to avoid tight error loops
            time.sleep(5)

def process_expired_containers(batch_size):
    """Process expired containers in batches to avoid overwhelming resources."""
    start_time = time.time()
    current_time = int(start_time)
    total_processed = 0
    total_removed = 0
    total_errors = 0
    
    try:
        # Get expired containers from database
        expired_containers = get_expired_containers(current_time)
        
        if not expired_containers:
            return
        
        total_to_process = len(expired_containers)
        logger.info(f"Found {total_to_process} expired containers to clean up")
        
        # Process in batches
        for i in range(0, total_to_process, batch_size):
            batch = expired_containers[i:i+batch_size]
            
            # Process each container in batch
            for container in batch:
                container_id, port = container[:2]
                try:
                    remove_container(container_id, port)
                    total_removed += 1
                except Exception as e:
                    logger.error(f"Error removing container {container_id}: {str(e)}")
                    total_errors += 1
                
                total_processed += 1
                
            # Log batch progress
            logger.info(f"Processed batch of {len(batch)} containers, "
                        f"{total_processed}/{total_to_process} total")
            
            # Brief pause between batches to avoid resource spikes
            if i + batch_size < total_to_process:
                time.sleep(1)
        
        duration = time.time() - start_time
        logger.info(f"Cleanup complete: processed {total_processed} containers "
                   f"({total_removed} removed, {total_errors} errors) in {duration:.2f}s")
    
    except Exception as e:
        logger.error(f"Error processing expired containers: {str(e)}")

def get_expired_containers(current_time):
    """Get all containers that have expired from the database."""
    conn = None
    try:
        conn = get_maintenance_connection()
        with conn.cursor() as cursor:
            # Find all containers that have expired
            cursor.execute("""
                SELECT id, port
                FROM containers
                WHERE expiration_time < %s
                ORDER BY expiration_time ASC
            """, (current_time,))
            
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error getting expired containers: {str(e)}")
        return []
    finally:
        if conn:
            release_maintenance_connection(conn)

def remove_container(container_id, port):
    """Remove a container from Docker and the database."""
    # First try to remove from Docker
    try:
        container = docker_client.containers.get(container_id)
        container.remove(force=True)
        logger.info(f"Removed container {container_id} from Docker")
    except docker.errors.NotFound:
        logger.warning(f"Container {container_id} not found in Docker, proceeding with database cleanup")
    except Exception as e:
        logger.error(f"Error removing container {container_id} from Docker: {str(e)}")
        # We continue to database cleanup even if Docker removal fails

    # Then clean up database records
    conn = None
    try:
        conn = get_maintenance_connection()
        
        # First release the port
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE port_allocations 
                SET allocated = FALSE, 
                    container_id = NULL, 
                    allocated_time = NULL 
                WHERE port = %s
            """, (port,))
        
        # Then remove container record
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM containers WHERE id = %s", (container_id,))
        
        conn.commit()
        logger.info(f"Removed container {container_id} from database and released port {port}")
        return True
    except Exception as e:
        logger.error(f"Error removing container {container_id} from database: {str(e)}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise
    finally:
        if conn:
            release_maintenance_connection(conn)

def shutdown():
    """Shutdown the cleanup manager, stopping the cleanup thread."""
    global cleanup_thread, stop_signal, maintenance_pool
    
    logger.info("Shutting down cleanup manager...")
    
    # Signal cleanup thread to stop
    stop_signal.set()
    
    # Wait for cleanup thread to finish
    if cleanup_thread and cleanup_thread.is_alive():
        cleanup_thread.join(timeout=5)
    
    # Close maintenance connection pool
    if maintenance_pool:
        try:
            maintenance_pool.closeall()
            logger.info("Closed maintenance connection pool")
        except Exception as e:
            logger.error(f"Error closing maintenance connection pool: {str(e)}")
    
    logger.info("Cleanup manager shutdown complete")
