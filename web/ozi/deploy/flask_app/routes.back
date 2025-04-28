from flask import Flask, jsonify, render_template, request, make_response
import threading
import time
import uuid
import docker
import logging
import os
import random, string, time
from datetime import datetime
from database import (
    execute_query, record_ip_request, check_ip_rate_limit, 
    get_container_by_uuid, store_container, remove_container_from_db,
    allocate_port, release_port, get_connection_pool_stats, perform_maintenance
)
from docker_utils import (
    client, 
    create_and_start_container,
    monitor_container,  # Updated to use thread pool instead of direct thread creation
    remove_container, 
    get_container_status, 
    get_container_security_options, 
    get_container_capabilities, 
    get_container_tmpfs,
    get_service_logs,
    get_all_service_logs,
)
from config import (
    IMAGES_NAME, LEAVE_TIME, ADD_TIME, FLAG, PORT_IN_CONTAINER, 
    CHALLENGE_TITLE, CHALLENGE_DESCRIPTION, COMMAND_CONNECT, CONTAINER_MEMORY_LIMIT,
    CONTAINER_SWAP_LIMIT, CONTAINER_CPU_LIMIT, CONTAINER_PIDS_LIMIT,
    ENABLE_READ_ONLY, MAX_CONTAINERS_PER_HOUR, RATE_LIMIT_WINDOW,
    NETWORK_NAME, BYPASS_CAPTCHA, MAINTENANCE_INTERVAL, ENABLE_RESOURCE_QUOTAS, DB_HOST, DB_NAME, ENABLE_LOGS_ENDPOINT, PORT_ALLOCATION_MAX_ATTEMPTS
)
from ctf_captcha import create_captcha, validate_captcha
import resource_monitor
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import metrics

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ctf-deployer')

# Define cookie name
COOKIE_NAME = 'user_uuid'

# Maintenance thread reference
maintenance_thread = None

# Create a periodic maintenance timer for cleanup operations
def start_maintenance_timer(interval=None):
    """
    Start a periodic maintenance timer for cleanup operations
    
    Args:
        interval: Interval in seconds between maintenance runs (defaults to MAINTENANCE_INTERVAL)
    
    Returns:
        The maintenance thread object
    """
    if interval is None:
        interval = MAINTENANCE_INTERVAL
        
    def maintenance_task():
        while True:
            try:
                logger.info("Running scheduled maintenance tasks...")
                perform_maintenance()
                logger.info("Scheduled maintenance completed")
            except Exception as e:
                logger.error(f"Error during scheduled maintenance: {str(e)}")
                # Record error in metrics
                metrics.ERRORS_TOTAL.labels(error_type='maintenance').inc()
            time.sleep(interval)
    
    thread = threading.Thread(target=maintenance_task, daemon=True)
    thread.start()
    logger.info(f"Started maintenance timer with {interval}s interval")
    return thread

def is_local_network(ip_address):
    """
    Check if the IP address belongs to a local network
    - 127.x.x.x (localhost)
    - 10.x.x.x (private class A)
    - 172.16.x.x - 172.31.x.x (private class B, includes Docker networks)
    - 192.168.x.x (private class C)
    - ::1 (localhost IPv6)
    """
    if not ip_address:
        return False
        
    # Check for localhost
    if ip_address in ('127.0.0.1', 'localhost', '::1'):
        return True
        
    # Check for RFC1918 private networks
    if ip_address.startswith('10.'):
        return True
        
    if ip_address.startswith('192.168.'):
        return True
        
    # Check for Docker's default network range
    if ip_address.startswith('172.'):
        try:
            # Extract the second octet to check if it's in the private range (16-31)
            second_octet = int(ip_address.split('.')[1])
            if 16 <= second_octet <= 31:
                return True
        except (ValueError, IndexError):
            pass
    
    return False

def check_admin_auth(request, admin_only=True):
    """
    Check if the request is authorized based on admin key or network
    
    Args:
        request: Flask request object
        admin_only: If True, requires admin key except for local networks
                   If False, allows local networks without admin key
    
    Returns:
        (bool, str): (is_authorized, error_message)
    """
    admin_key = request.args.get('admin_key', '')
    expected_admin_key = os.environ.get('ADMIN_KEY', '')
    
    # Validate admin key if provided
    if admin_key and admin_key == expected_admin_key:
        return True, None
    
    # Check network address
    if not admin_only or is_local_network(request.remote_addr):
        return True, None
        
    # Not authorized
    return False, "Unauthorized. Access restricted to local network or with valid admin key"


@app.template_filter('to_datetime')
def to_datetime_filter(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

@app.route("/")
def index():
    user_uuid = request.cookies.get(COOKIE_NAME)
    
    # Get server hostname for the template
    hostname = request.host.split(':')[0] if ':' in request.host else request.host
    con_host = COMMAND_CONNECT.replace('<ip>', hostname)
    is_localhost = hostname == '127.0.0.1' or hostname == 'localhost'

    # Determine protocol (http by default)
    protocol = "http"
    
    logger.info(f"Index accessed by {request.remote_addr} - Using protocol: {protocol} for hostname: {hostname}")

    if not user_uuid:
        user_uuid = str(uuid.uuid4())
        logger.info(f"Creating new user UUID: {user_uuid}")
        response = make_response(render_template("index.html", 
                                               user_container=None, 
                                               add_minutes=(ADD_TIME // 60),
                                               hostname=con_host,
                                               protocol=protocol,
                                               challenge_title=CHALLENGE_TITLE,
                                               challenge_description=CHALLENGE_DESCRIPTION,
                                               bypass_captcha=BYPASS_CAPTCHA))
        
        # For localhost development, we need less strict cookie settings
        if is_localhost:
            # Development environment - more permissive cookies
            response.set_cookie(COOKIE_NAME, user_uuid, httponly=True, samesite='Lax')
        else:
            # Production environment - less strict cookies for better compatibility
            response.set_cookie(COOKIE_NAME, user_uuid, httponly=True, secure=False, samesite='Lax')
        return response

    logger.info(f"Existing user UUID: {user_uuid}")
    user_container = get_container_by_uuid(user_uuid)
    
    # If container exists, check its actual status
    container_status = None
    if user_container:
        container_status = get_container_status(user_container[0])
        con_host = COMMAND_CONNECT.replace('<ip>', hostname).replace('<port>', str(user_container[1]))
    
    response = make_response(render_template("index.html", 
                                           user_container=user_container, 
                                           container_status=container_status,
                                           add_minutes=(ADD_TIME // 60),
                                           hostname=con_host,
                                           protocol=protocol,
                                           challenge_title=CHALLENGE_TITLE,
                                           challenge_description=CHALLENGE_DESCRIPTION,
                                           bypass_captcha=BYPASS_CAPTCHA))
    return response

@app.route("/get_captcha", methods=["GET"])
def get_captcha():
    """Generate a new CAPTCHA challenge"""
    captcha_id, captcha_image = create_captcha()
    # Record captcha generation in metrics
    metrics.CAPTCHA_GENERATED.inc()
    return jsonify({
        "captcha_id": captcha_id,
        "captcha_image": captcha_image
    })


def generate_unique_suffix(length=6):
    """Generate a random alphanumeric suffix (to ensure unique container names)."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


@app.route("/deploy", methods=["POST"])
def deploy_container():
    """Attempts to create + start a new container for the user, removing partial containers if start fails."""
    with metrics.TimingContext(metrics.CONTAINER_DEPLOYMENT_DURATION):
        try:
            # 1) Check for user_uuid cookie
            user_uuid = request.cookies.get(COOKIE_NAME)
            if not user_uuid:
                logger.error("No user_uuid cookie found")
                metrics.ERRORS_TOTAL.labels(error_type='session_error').inc()
                return jsonify({"error": "Session error: please refresh the page."}), 400
            
            remote_ip = request.remote_addr
            logger.info(f"Deploy request from IP={remote_ip}, UUID={user_uuid}")
            
            # 2) Rate-limiting
            if check_ip_rate_limit(remote_ip):
                logger.warning(f"Rate limit exceeded for IP={remote_ip}")
                return jsonify({"error": "You have reached your max containers for this period."}), 429
            
            # 3) Parse JSON, check captcha unless bypassed
            data = request.get_json()
            if not data:
                logger.error("No JSON data in request.")
                metrics.ERRORS_TOTAL.labels(error_type='invalid_request').inc()
                return jsonify({"error": "Invalid request format. No JSON data."}), 400
            
            captcha_id = data.get("captcha_id")
            captcha_answer = data.get("captcha_answer")
            
            # If not bypassing, validate the CAPTCHA
            if os.getenv('BYPASS_CAPTCHA', 'false').lower() == 'false':
                if not captcha_id or not captcha_answer:
                    logger.error("Missing captcha data")
                    metrics.ERRORS_TOTAL.labels(error_type='missing_captcha').inc()
                    return jsonify({"error": "CAPTCHA verification required"}), 400
                
                if not validate_captcha(captcha_id, captcha_answer):
                    logger.error(f"Incorrect captcha answer: {captcha_answer}")
                    metrics.ERRORS_TOTAL.labels(error_type='invalid_captcha').inc()
                    return jsonify({"error": "Incorrect CAPTCHA answer"}), 400
                
                # Record success
                metrics.CAPTCHA_VALIDATIONS.inc()
            else:
                logger.info("BYPASS_CAPTCHA enabled, skipping CAPTCHA check.")
            
            # 4) Ensure user doesn't already have a running container
            existing = get_container_by_uuid(user_uuid)
            if existing:
                logger.warning(f"User {user_uuid} already has container {existing[0]}")
                metrics.ERRORS_TOTAL.labels(error_type='duplicate_container').inc()
                return jsonify({"error": "You already have a running container"}), 400
            
            # 5) If resource quotas, verify system usage
            if ENABLE_RESOURCE_QUOTAS:
                container_cpu = float(CONTAINER_CPU_LIMIT) * 100
                container_memory = float(CONTAINER_MEMORY_LIMIT.rstrip('M')) / 1024.0  # MB -> GB
                metrics.RESOURCE_QUOTA_CHECKS.inc()
                
                ok, msg = resource_monitor.check_resource_availability(
                    container_cpu=container_cpu,
                    container_memory=container_memory
                )
                if not ok:
                    logger.warning(f"Resource limit hit: {msg}")
                    return jsonify({"error": f"Resource limit reached: {msg}"}), 503
            
            # 6) Build a unique container name
            base_project_name = os.getenv('COMPOSE_PROJECT_NAME', 'ctf_task')
            safe_user = user_uuid.replace('-', '_')
            time_stamp = int(time.time())
            rand_suffix = generate_unique_suffix(4)
            container_name = f"{base_project_name}_session_{safe_user}_{time_stamp}_{rand_suffix}"
            
            expiration_time = time.time() + LEAVE_TIME
            blocked_ports = []
            final_container = None
            
            # We'll try up to PORT_ALLOCATION_MAX_ATTEMPTS to find a port that doesn't fail
            for attempt_i in range(PORT_ALLOCATION_MAX_ATTEMPTS):
                # allocate_port supports blocked_ports to skip ones that failed
                port = allocate_port(container_id=None, blocked_ports=blocked_ports)
                if not port:
                    logger.error("No available ports in the DB or all are blocked.")
                    return jsonify({"error": "No free ports. Please try again later."}), 503
                
                logger.info(f"Trying port={port} for container name={container_name} (attempt {attempt_i+1}).")
                
                # Prepare container config for creation (no start yet)
                config = {
                    'image': IMAGES_NAME,
                    'name': container_name,
                    'detach': True,
                    'ports': {f"{PORT_IN_CONTAINER}/tcp": port},
                    'environment': {'FLAG': FLAG},
                    'network': os.getenv('NETWORK_NAME', 'bridge'),
                    'mem_limit': CONTAINER_MEMORY_LIMIT,
                    'memswap_limit': CONTAINER_SWAP_LIMIT,
                    'cpu_period': 100000,
                    'cpu_quota': int(100000 * float(CONTAINER_CPU_LIMIT)),
                    'pids_limit': int(CONTAINER_PIDS_LIMIT),
                    'read_only': (ENABLE_READ_ONLY),
                    'security_opt': get_container_security_options(),
                }
                
                # Additional capabilities or tmpfs
                cap = get_container_capabilities()
                if cap['drop_all']:
                    config['cap_drop'] = ['ALL']
                    config['cap_add'] = cap['add']
                tmpfs_conf = get_container_tmpfs()
                if tmpfs_conf:
                    config['tmpfs'] = tmpfs_conf
                
                # Attempt the 2-step create+start
                try:
                    final_container = create_and_start_container(config)
                    # If we got here, the container started successfully (port wasn't blocked externally)
                    logger.info(f"Container {final_container.id} fully started on port {port}.")
                    break  # success
                except docker.errors.APIError as e:
                    # Could be address in use or something else
                    if "address already in use" in str(e).lower():
                        logger.warning(f"Port {port} is in use externally. Releasing & skipping it.")
                        release_port(port)
                        blocked_ports.append(port)
                        final_container = None
                        # Move on to next attempt
                        continue
                    else:
                        logger.error(f"Container creation+start error (not address in use): {str(e)}")
                        release_port(port)
                        return jsonify({"error": f"Docker error: {str(e)}"}), 500
            
            # If we never successfully started a container, fail
            if not final_container:
                logger.error("All attempts exhausted without success, container not started.")
                return jsonify({"error": "All attempted ports failed. Try again later."}), 503
            
            # 7) store container in DB
            try:
                record_ip_request(remote_ip)
                now_ts = int(time.time())
                success = store_container(
                    final_container.id,
                    port,
                    user_uuid,
                    remote_ip,
                    int(now_ts + LEAVE_TIME)
                )
                if not success:
                    raise Exception("DB insert returned false.")
                
                metrics.CONTAINER_DEPLOYMENTS_TOTAL.inc()
            except Exception as db_err:
                logger.error(f"Error storing container in DB: {db_err}")
                metrics.ERRORS_TOTAL.labels(error_type='container_recording').inc()
                # Clean up container
                try:
                    final_container.remove(force=True)
                    release_port(port)
                except Exception as cleanup_e:
                    logger.error(f"Failed to remove container after DB error: {cleanup_e}")
                return jsonify({"error": "Internal DB error storing container info."}), 500
            
            # 8) success
            return jsonify({
                "message": "Your challenge is ready!",
                "port": port,
                "id": final_container.id,
                "expiration_time": int(time.time() + LEAVE_TIME)
            })
        
        except Exception as e:
            # Catch any unexpected unhandled error
            logger.error(f"Unhandled error in deploy_container: {str(e)}")
            metrics.ERRORS_TOTAL.labels(error_type='unhandled').inc()
            return jsonify({"error": f"Unhandled error: {str(e)}"}), 500

@app.route("/stop", methods=["POST"])
def stop_container():
    user_uuid = request.cookies.get(COOKIE_NAME)
    
    if not user_uuid:
        metrics.ERRORS_TOTAL.labels(error_type='session_error').inc()
        return jsonify({"error": "Session error. Please refresh the page."}), 400

    try:
        container_data = execute_query("SELECT id, port FROM containers WHERE user_uuid = %s", (user_uuid,), fetchone=True)
        if not container_data:
            metrics.ERRORS_TOTAL.labels(error_type='no_container').inc()
            return jsonify({"error": "No active container"}), 400

        container_id, port = container_data

        # Record container lifetime
        try:
            # Get start time from database
            container_info = execute_query(
                "SELECT start_time FROM containers WHERE id = %s",
                (container_id,),
                fetchone=True
            )
            if container_info and container_info[0]:
                start_time = container_info[0]
                lifetime = time.time() - start_time
                metrics.CONTAINER_LIFETIME.observe(lifetime)
        except Exception as e:
            logger.error(f"Error recording container lifetime: {str(e)}")

        remove_container(container_id, port)
        return jsonify({"message": "Challenge instance stopped successfully"})
    except Exception as e:
        logger.error(f"Error in stop_container: {str(e)}")
        metrics.ERRORS_TOTAL.labels(error_type='container_stop').inc()
        return jsonify({"error": f"Failed to stop container: {str(e)}"}), 500

@app.route("/restart", methods=["POST"])
def restart_container():
    user_uuid = request.cookies.get(COOKIE_NAME)
    
    if not user_uuid:
        metrics.ERRORS_TOTAL.labels(error_type='session_error').inc()
        return jsonify({"error": "Session error. Please refresh the page."}), 400

    try:
        container_data = execute_query("SELECT id FROM containers WHERE user_uuid = %s", (user_uuid,), fetchone=True)
        if not container_data:
            metrics.ERRORS_TOTAL.labels(error_type='no_container').inc()
            return jsonify({"error": "No active container"}), 400
        
        container_id = container_data[0]
        
        container = client.containers.get(container_id)
        container.restart()
        
        # Record container restart
        metrics.CONTAINER_RESTARTS.inc()
        
        return jsonify({"message": "Challenge instance restarted successfully"})
    except docker.errors.NotFound:
        metrics.ERRORS_TOTAL.labels(error_type='container_not_found').inc()
        return jsonify({"error": "Container not found"}), 404
    except Exception as e:
        logger.error(f"Error in restart_container: {str(e)}")
        metrics.ERRORS_TOTAL.labels(error_type='container_restart').inc()
        return jsonify({"error": f"Failed to restart container: {str(e)}"}), 500

@app.route("/extend", methods=["POST"])
def extend_container_lifetime():
    user_uuid = request.cookies.get(COOKIE_NAME)
    
    if not user_uuid:
        metrics.ERRORS_TOTAL.labels(error_type='session_error').inc()
        return jsonify({"error": "Session error. Please refresh the page."}), 400

    try:
        container_data = execute_query("SELECT id, expiration_time FROM containers WHERE user_uuid = %s", (user_uuid,), fetchone=True)
        if not container_data:
            metrics.ERRORS_TOTAL.labels(error_type='no_container').inc()
            return jsonify({"error": "No active container"}), 400
            
        container_id, expiration_time = container_data
        
        # Increase container lifetime by ADD_TIME
        new_expiration_time = expiration_time + ADD_TIME
        
        # Update lifetime in database - use execute_insert
        execute_query(
            "UPDATE containers SET expiration_time = %s WHERE id = %s", 
            (new_expiration_time, container_id)
        )
        
        # Record container lifetime extension
        metrics.CONTAINER_LIFETIME_EXTENSIONS.inc()
        
        return jsonify({
            "message": f"Challenge lifetime extended by {ADD_TIME // 60} minutes!", 
            "new_expiration_time": new_expiration_time
        })
    except Exception as e:
        logger.error(f"Error in extend_container_lifetime: {str(e)}")
        metrics.ERRORS_TOTAL.labels(error_type='container_extend').inc()
        return jsonify({"error": f"Failed to extend container lifetime: {str(e)}"}), 500

@app.route("/admin")
def admin_panel():
    """Admin panel for monitoring and management"""
    return render_template("admin.html")

@app.route("/admin/status")
def admin_status():
    """Combined status endpoint with detailed information about the deployer service"""
    try:
        # Security check - verify admin key or localhost
        admin_key = request.args.get('admin_key', '')
        is_localhost = request.remote_addr in ('127.0.0.1', 'localhost', '::1')
        is_docker_network = request.remote_addr.startswith('172.')  # Docker's default network
        expected_admin_key = os.environ.get('ADMIN_KEY', '')
        
        # Allow access from localhost or Docker network without key, or with valid key from anywhere
        if not (is_localhost or is_docker_network) and admin_key != expected_admin_key:
            logger.warning(f"Unauthorized status access attempt from {request.remote_addr}")
            metrics.ERRORS_TOTAL.labels(error_type='unauthorized_access').inc()
            return jsonify({"error": "Unauthorized. Access restricted to local network or with valid admin key"}), 403
        
        # Basic info always included
        basic_info = {
            "status": "online",
            "service": "CTF Challenge Deployer",
            "version": "1.2",
            "challenge": CHALLENGE_TITLE
        }
        
        # Get database statistics and active containers
        active_containers = execute_query("SELECT COUNT(*) FROM containers", fetchone=True)[0]
        total_containers_created = execute_query("SELECT COUNT(*) FROM ip_requests", fetchone=True)[0]
        
        # Get database connection pool stats
        pool_stats = get_connection_pool_stats()
        
        # Count available ports
        available_ports = execute_query(
            "SELECT COUNT(*) FROM port_allocations WHERE allocated = FALSE", 
            fetchone=True
        )[0]
        
        total_ports = execute_query(
            "SELECT COUNT(*) FROM port_allocations", 
            fetchone=True
        )[0]
        
        # Get resource usage stats if resource quotas are enabled
        resource_stats = {}
        if ENABLE_RESOURCE_QUOTAS:
            usage = resource_monitor.get_resource_usage()
            resource_stats = {
                "status": usage["status"],
                "containers": {
                    "current": usage["containers"]["current"],
                    "limit": usage["containers"]["limit"],
                    "percent": f"{usage['containers']['percent']:.1f}%"
                },
                "cpu": {
                    "current": f"{usage['cpu']['current']:.1f}%",
                    "limit": f"{usage['cpu']['limit']}%",
                    "percent": f"{usage['cpu']['percent']:.1f}%"
                },
                "memory": {
                    "current": f"{usage['memory']['current']:.2f} GB",
                    "limit": f"{usage['memory']['limit']} GB",
                    "percent": f"{usage['memory']['percent']:.1f}%"
                },
                "last_updated": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(usage["last_updated"]))
            }
        
        # Active containers details (only in detailed view)
        active_container_details = []
        try:
            containers = execute_query("SELECT id, port, start_time, expiration_time, user_uuid, ip_address FROM containers")
            for container in containers:
                container_id, port, start_time, exp_time, user_uuid, ip_address = container
                container_detail = {
                    "id": container_id[:12] + "...",  # Truncate for display
                    "full_id": container_id,
                    "port": port,
                    "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
                    "expiration_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp_time)),
                    "time_left": exp_time - int(time.time()),
                    "user_uuid": user_uuid,
                    "ip_address": ip_address
                }
                
                # Try to get container status from Docker
                try:
                    container_status = get_container_status(container_id)
                    container_detail["status"] = container_status.get('status', 'unknown')
                    container_detail["running"] = container_status.get('running', False)
                except:
                    container_detail["status"] = "error"
                    container_detail["running"] = False
                
                active_container_details.append(container_detail)
        except Exception as e:
            logger.error(f"Error getting container details: {str(e)}")
            active_container_details = [{"error": str(e)}]
        
        # Rate limit info
        rate_limit_info = {
            "max_containers_per_hour": MAX_CONTAINERS_PER_HOUR,
            "window_seconds": RATE_LIMIT_WINDOW
        }
        
        # Build combined response
        response = {
            **basic_info,
            "metrics": {
                "active_containers": active_containers,
                "total_containers_created": total_containers_created,
                "available_ports": available_ports,
                "total_ports": total_ports,
                "port_usage_percent": f"{(total_ports - available_ports) / total_ports * 100:.1f}%" if total_ports > 0 else "0%"
            },
            "database": {
                "connection_pool": pool_stats,
                "host": DB_HOST,
                "name": DB_NAME
            },
            "resources": resource_stats,
            "rate_limiting": rate_limit_info,
            "containers": active_container_details
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in admin status endpoint: {str(e)}")
        metrics.ERRORS_TOTAL.labels(error_type='status_endpoint').inc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/status")
def status():
    """Basic status endpoint - redirects to admin status with full info if admin key provided"""
    admin_key = request.args.get('admin_key', '')
    if admin_key:
        return admin_status()
    
    # Basic status info only
    try:
        # Basic info always included
        basic_info = {
            "status": "online",
            "service": "CTF Challenge Deployer",
            "challenge": CHALLENGE_TITLE,
            "message": "For detailed status, use /admin/status endpoint with admin key"
        }
        
        return jsonify(basic_info)
    except Exception as e:
        logger.error(f"Error in status endpoint: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/health")
def health_check():
    """Simple health check endpoint for monitoring systems"""
    return jsonify({"status": "healthy"})

@app.route('/metrics')
def metrics_endpoint():
    """Expose Prometheus metrics with security controls"""
    try:
        # Check authorization
        is_authorized, error_message = check_admin_auth(request)
        if not is_authorized:
            logger.warning(f"Unauthorized metrics access attempt from {request.remote_addr}")
            return jsonify({"error": error_message}), 403
        
        # Update database connection pool metrics before generating response
        try:
            pool_stats = get_connection_pool_stats()
            metrics.update_db_connection_metrics(pool_stats)
        except Exception as e:
            logger.error(f"Error updating database metrics: {str(e)}")
            # Continue despite error - we can still return other metrics
        
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as e:
        logger.error(f"Error generating metrics: {str(e)}")
        metrics.ERRORS_TOTAL.labels(error_type='metrics_endpoint').inc()
        return jsonify({"error": "Error generating metrics"}), 500

@app.route('/logs')
def logs_endpoint():
    """Enhanced logs endpoint that provides access to user containers and service logs
    
    Parameters:
    - container_id: Container ID to get logs for, special values include:
        - "deployer" - For flask_app logs
        - "database" - For postgres logs
        - "task_service" - For generic_task logs
        - "all_services" - For all service logs
        - empty/not specified - For all user containers
    - tail: Number of lines to retrieve (default: 100)
    - since: Timestamp to fetch logs since (in seconds since epoch)
    - admin_key: Admin key for authentication from non-localhost
    - format: Output format ('json' or 'text', default: 'json')
    """
    try:
        # Check if logs endpoint is enabled
        if not ENABLE_LOGS_ENDPOINT:
            return jsonify({"error": "Logs endpoint is disabled"}), 404
        
        # Check authorization
        is_authorized, error_message = check_admin_auth(request)
        if not is_authorized:
            logger.warning(f"Unauthorized logs access attempt from {request.remote_addr}")
            return jsonify({"error": error_message}), 403
        
        # Get request parameters
        container_id = request.args.get('container_id', None)
        tail = request.args.get('tail', '100')
        since = request.args.get('since', None)  # Time since epoch in seconds
        output_format = request.args.get('format', 'json').lower()
        
        # Validate tail parameter
        try:
            tail = int(tail)
            if tail < 1:
                tail = 100
        except (ValueError, TypeError):
            tail = 100
        
        # Convert since parameter to timestamp
        since_timestamp = None
        if since:
            try:
                since_timestamp = int(since)
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid 'since' parameter. Expected Unix timestamp (seconds)"}), 400
        
        # Check if request is for a service container
        service_containers = ['deployer', 'database', 'task_service', 'all_services']
        
        if container_id in service_containers:
            return handle_service_logs(container_id, tail, since_timestamp, output_format)
        elif container_id and container_id.lower() == "all":
            return handle_all_logs(tail, since_timestamp, output_format)
        else:
            return handle_user_container_logs(container_id, tail, since_timestamp, output_format)
    
    except Exception as e:
        logger.error(f"Unhandled error in logs endpoint: {str(e)}")
        metrics.ERRORS_TOTAL.labels(error_type='logs_endpoint').inc()
        return jsonify({"error": "Internal server error"}), 500

def handle_service_logs(service_id, tail, since_timestamp, output_format):
    """Handle logs for service containers"""
    try:
        # Special handling for all_services
        if service_id == 'all_services':
            # Get logs for all services
            logs_by_service = get_all_service_logs(tail, since_timestamp)
            
            if output_format == 'text':
                # Format as text with service headers
                text_output = ""
                for service_name, logs in logs_by_service.items():
                    text_output += f"\n===== Service: {service_name} =====\n"
                    text_output += logs
                    text_output += "\n\n"
                
                return text_output, 200, {'Content-Type': 'text/plain'}
            else:
                # Return as JSON
                return jsonify({
                    "services": logs_by_service
                })
        else:
            # Get logs for specific service
            logs = get_service_logs(service_id, tail, since_timestamp)
            
            if logs is None:
                return jsonify({"error": f"Service '{service_id}' not found or logs unavailable"}), 404
                
            if output_format == 'text':
                return logs, 200, {'Content-Type': 'text/plain'}
            else:
                return jsonify({
                    "service": service_id,
                    "logs": logs.splitlines() if logs else []
                })
    except Exception as e:
        logger.error(f"Error handling service logs: {str(e)}")
        return jsonify({"error": f"Failed to retrieve service logs: {str(e)}"}), 500

def handle_all_logs(tail, since_timestamp, output_format):
    """Handle logs for all containers and services"""
    try:
        # Get service logs
        service_logs = get_all_service_logs(tail, since_timestamp)
        
        # Get user container logs
        user_container_logs = {}
        containers = execute_query("SELECT id FROM containers")
        
        for container_data in containers:
            container_id = container_data[0]
            try:
                container = client.containers.get(container_id)
                log_data = container.logs(
                    tail=tail,
                    since=since_timestamp,
                    timestamps=True
                ).decode('utf-8', errors='replace')
                
                user_container_logs[container_id] = log_data.splitlines() if output_format == 'json' else log_data
            except docker.errors.NotFound:
                user_container_logs[container_id] = ["Container not found in Docker"]
            except Exception as e:
                user_container_logs[container_id] = [f"Error retrieving logs: {str(e)}"]
        
        # Combine results
        if output_format == 'text':
            text_output = ""
            
            # Add service logs
            for service_name, logs in service_logs.items():
                text_output += f"\n===== Service: {service_name} =====\n"
                text_output += logs
                text_output += "\n\n"
            
            # Add user container logs
            for container_id, logs in user_container_logs.items():
                text_output += f"\n===== User Container: {container_id} =====\n"
                text_output += logs if isinstance(logs, str) else "\n".join(logs)
                text_output += "\n\n"
            
            return text_output, 200, {'Content-Type': 'text/plain'}
        else:
            # Return as JSON
            return jsonify({
                "services": service_logs,
                "containers": user_container_logs
            })
    except Exception as e:
        logger.error(f"Error handling all logs: {str(e)}")
        return jsonify({"error": f"Failed to retrieve logs: {str(e)}"}), 500

def handle_user_container_logs(container_id, tail, since_timestamp, output_format):
    """Handle logs for user containers (original functionality)"""
    try:
        # Handle specific container
        if container_id:
            # Check if container exists in our database
            container_data = execute_query(
                "SELECT id FROM containers WHERE id = %s", 
                (container_id,),
                fetchone=True
            )
            
            if not container_data:
                return jsonify({"error": f"Container {container_id} not found or not managed by this deployer"}), 404
            
            # Get logs for this specific container
            try:
                container = client.containers.get(container_id)
                log_data = container.logs(
                    tail=tail,
                    since=since_timestamp,
                    timestamps=True
                ).decode('utf-8', errors='replace')
                
                if output_format == 'text':
                    return log_data, 200, {'Content-Type': 'text/plain'}
                else:
                    return jsonify({
                        "container_id": container_id,
                        "logs": log_data.splitlines()
                    })
            except docker.errors.NotFound:
                return jsonify({"error": f"Container {container_id} not found in Docker"}), 404
            except Exception as e:
                logger.error(f"Error getting logs for container {container_id}: {str(e)}")
                return jsonify({"error": f"Failed to get logs: {str(e)}"}), 500
        else:
            # Get all user containers
            try:
                containers = execute_query("SELECT id FROM containers")
                
                # No containers found
                if not containers:
                    return jsonify({"message": "No active containers found", "containers": {}})
                
                # Collect logs for all containers
                logs_by_container = {}
                
                for container_data in containers:
                    container_id = container_data[0]
                    try:
                        container = client.containers.get(container_id)
                        log_data = container.logs(
                            tail=tail,
                            since=since_timestamp,
                            timestamps=True
                        ).decode('utf-8', errors='replace')
                        
                        logs_by_container[container_id] = log_data.splitlines() if output_format == 'json' else log_data
                    except docker.errors.NotFound:
                        logs_by_container[container_id] = ["Container not found in Docker"]
                    except Exception as e:
                        logs_by_container[container_id] = [f"Error retrieving logs: {str(e)}"]
                
                if output_format == 'text':
                    # Merge all logs with container identifiers
                    text_output = ""
                    for container_id, logs in logs_by_container.items():
                        text_output += f"\n===== Container: {container_id} =====\n"
                        text_output += logs if isinstance(logs, str) else "\n".join(logs)
                        text_output += "\n\n"
                    
                    return text_output, 200, {'Content-Type': 'text/plain'}
                else:
                    return jsonify({
                        "containers": logs_by_container
                    })
                
            except Exception as e:
                logger.error(f"Error retrieving container logs: {str(e)}")
                return jsonify({"error": f"Failed to retrieve logs: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Error handling user container logs: {str(e)}")
        return jsonify({"error": f"Failed to retrieve logs: {str(e)}"}), 500
