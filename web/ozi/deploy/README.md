# 🚀 CTF Challenge Deployer

![Version](https://img.shields.io/badge/version-1.2-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A flexible, containerized solution for deploying Capture The Flag (CTF) challenges with isolated instances for each participant.

## 📋 Overview

This system provides an easy way to deploy containerized CTF challenges for competitions, training, or educational purposes. Each participant gets their own isolated container instance with:

- ⏱️ Automatic expiration 
- ⌛ Session extension capability
- 🔄 Container restart functionality
- 🛡️ Isolated environments to prevent interference between participants

## ✨ Features

- **🔒 Isolated Environments**: Each user receives a dedicated containerized challenge instance
- **⚙️ Highly Configurable**: All settings configurable through a single `.env` file
- **🌐 Web Interface**: Simple UI for container management
- **🤖 CAPTCHA Protection**: Prevents automated abuse
- **🔄 Auto-cleanup**: Automatically removes expired containers
- **📊 Resource Limiting**: Control CPU, memory, and process limits
- **🛡️ Security Options**: Customizable security settings for containers
- **📈 Rate Limiting**: Prevents abuse by limiting containers per IP address
- **🌍 Network Isolation**: Dedicated network for challenge instances

## 🏛️ Architecture

The system consists of two main components:

1. **Flask Application (Deployer)**: Web interface for managing challenge instances
2. **Challenge Container**: Docker container with the actual CTF challenge

```
                ┌───────────────┐
                │    User Web   │
                │    Browser    │
                └───────┬───────┘
                        │
                        ▼
┌──────────────────────────────────────┐
│            Flask Deployer            │
│                                      │
│  ┌─────────────┐    ┌─────────────┐  │
│  │Web Interface│◄───┤ Docker API  │  │
│  └─────────────┘    └──────┬──────┘  │
└──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────┐
│           Docker Network             │
│                                      │
│    ┌─────────┐  ┌─────────┐          │
│    │Container│  │Container│   ...    │
│    │    1    │  │    2    │          │
│    └─────────┘  └─────────┘          │
└──────────────────────────────────────┘
```

## 📥 Installation

### Requirements

- Docker and Docker Compose
- Git (for cloning the repository)

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/g-verdex/ctf-deployer.git
   cd ctf-deployer
   ```

2. Configure your environment:
   ```bash
   # Create or modify the .env file as needed
   nano .env
   ```

3. Run the deployment script with root privileges:
   ```bash
   chmod +x deploy.sh
   sudo ./deploy.sh up
   ```

4. Access the deployer:
   ```
   http://localhost:6664 (or your configured FLASK_APP_PORT)
   ```

## ⚙️ Configuration

All configuration is done through the `.env` file. The system validates all required variables during startup to ensure proper operation.

### ⚠️ Avoiding Conflicts When Running Multiple CTF Challenges

When running multiple CTF challenge deployments on the same host, it's critical to configure each with unique values for the following variables:

| Variable | Recommendation | Potential Conflict |
|----------|---------------|-------------------|
| `COMPOSE_PROJECT_NAME` | Use a unique name for each challenge type | Container name conflicts |
| `IMAGES_NAME` | **Important:** Use `localhost/{challenge_name}:latest` format | Image overwriting, breaking other deployments |
| `START_RANGE`/`STOP_RANGE` | Use non-overlapping port ranges for each deployment | Port conflicts |
| `FLASK_APP_PORT` | Must be unique for each deployment | Port conflicts |
| `DIRECT_TEST_PORT` | Must be unique for each deployment | Port conflicts |
| `NETWORK_NAME` | Use a unique name for each challenge | Network conflicts |
| `NETWORK_SUBNET` | Use non-overlapping subnets (e.g., 172.21.0.0/22, 172.21.4.0/22) | Network routing issues |
| `DB_PATH` | Can be shared if using same data directory, otherwise unique | Database corruption |

### Configuration Variable Best Practices

#### Container Identification
* `COMPOSE_PROJECT_NAME`: Use a descriptive name for your challenge (e.g., `xss_challenge`, `buffer_overflow`)
* `IMAGES_NAME`: **Critical** - Use `localhost/{COMPOSE_PROJECT_NAME}:latest` to avoid conflicts

#### Port Configuration
* `PORT_IN_CONTAINER`: The internal port your challenge listens on (usually 80 for web)
* `START_RANGE`/`STOP_RANGE`: Define a range with at least 100 ports to allow multiple instances
* Use non-overlapping ranges for different deployments:
  * Deployment 1: 7000-8000
  * Deployment 2: 8001-9000
  * Deployment 3: 9001-10000

#### Network Configuration
* `NETWORK_NAME`: Use a unique name including the challenge name
* `NETWORK_SUBNET`: Use separate subnets for each deployment:
  * 172.21.0.0/22
  * 172.21.4.0/22
  * 172.21.8.0/22
  * 172.21.12.0/22

### Complete Environment Variable Reference

#### Container Identification

| Variable | Description | Required | Best Practice |
|----------|-------------|----------|--------------|
| `COMPOSE_PROJECT_NAME` | Name prefix for Docker containers | Yes | Use a unique, descriptive name for each challenge |
| `IMAGES_NAME` | Docker image name for the challenge | Yes | Use format `localhost/{COMPOSE_PROJECT_NAME}:latest` |
| `FLAG` | CTF flag value to be passed to containers | Optional* | Can be empty if embedded in challenge |

> *Note: `FLAG` can be left as an empty string (`FLAG=""`) if you prefer to embed the flag directly in your challenge rather than passing it as an environment variable. Do not comment out this variable even if you leave it empty.

#### Time Settings

| Variable | Description | Required | Best Practice |
|----------|-------------|----------|--------------|
| `LEAVE_TIME` | Default container lifetime in seconds (e.g., 1800 for 30 minutes) | Yes | 1800-3600 is a reasonable balance |
| `ADD_TIME` | Additional time when extending container life in seconds (e.g., 600 for 10 minutes) | Yes | 600 is typically sufficient |

#### Port Configuration

| Variable | Description | Required | Best Practice |
|----------|-------------|----------|--------------|
| `PORT_IN_CONTAINER` | Port the challenge service runs on inside container | Yes | Standard ports (80, 8080, etc.) |
| `START_RANGE` | Start of port range for container mapping (e.g., 9000) | Yes | Non-overlapping with other deployments |
| `STOP_RANGE` | End of port range for container mapping (e.g., 10000) | Yes | At least 100-1000 ports per deployment |
| `FLASK_APP_PORT` | Port where the flask deployer app will be accessible | Yes | Unique for each deployment |
| `DIRECT_TEST_PORT` | Port for directly testing the challenge (bypassing deployer) | Yes | Unique for each deployment |

#### Network Configuration

| Variable | Description | Required | Best Practice |
|----------|-------------|----------|--------------|
| `NETWORK_NAME` | Docker network name for challenge containers | Yes | Include challenge name and a unique identifier |
| `NETWORK_SUBNET` | Subnet for the Docker network (e.g., 172.28.16.0/22) | Yes | Non-overlapping with other deployments |

#### Database Settings

| Variable | Description | Required | Best Practice |
|----------|-------------|----------|--------------|
| `DB_PATH` | Path to SQLite database file (e.g., ./data/containers.db) | Yes | Use a unique path per deployment |

#### Challenge Display

| Variable | Description | Required | Best Practice |
|----------|-------------|----------|--------------|
| `CHALLENGE_TITLE` | Title displayed to users in the web interface | Yes | Clear, descriptive title |
| `CHALLENGE_DESCRIPTION` | Challenge description shown to users | Yes | Include any hints and instructions |

#### Resource Limits

| Variable | Description | Required | Best Practice |
|----------|-------------|----------|--------------|
| `CONTAINER_MEMORY_LIMIT` | Maximum memory per container (e.g., 512M) | Yes | Balance between performance and capacity |
| `CONTAINER_SWAP_LIMIT` | Maximum swap memory per container (e.g., 512M) | Yes | Usually same as memory limit |
| `CONTAINER_CPU_LIMIT` | CPU cores allocated per container (e.g., 0.5 for half a core) | Yes | 0.5-1.0 for most challenges |
| `CONTAINER_PIDS_LIMIT` | Maximum process IDs per container (e.g., 100) | Yes | 100-200 is sufficient for most challenges |

#### Security Options

| Variable | Description | Required | Best Practice |
|----------|-------------|----------|--------------|
| `ENABLE_NO_NEW_PRIVILEGES` | Prevent privilege escalation (true/false) | Yes | true for most challenges |
| `ENABLE_READ_ONLY` | Make container filesystem read-only (true/false) | Yes | true if possible, false if challenge requires writes |
| `ENABLE_TMPFS` | Enable temporary filesystem (true/false) | Yes | true if ENABLE_READ_ONLY is true |
| `TMPFS_SIZE` | Size of tmpfs if enabled (e.g., 64M) | Yes | 64M-128M is typically sufficient |

#### Container Capabilities

| Variable | Description | Required | Best Practice |
|----------|-------------|----------|--------------|
| `DROP_ALL_CAPABILITIES` | Whether to drop all capabilities by default (true/false) | Yes | true for better security |
| `CAP_NET_BIND_SERVICE` | Allow binding to privileged ports <1024 (true/false) | Yes | true only if needed |
| `CAP_CHOWN` | Allow changing file ownership (true/false) | Yes | true only if needed |

#### Rate Limiting

| Variable | Description | Required | Best Practice |
|----------|-------------|----------|--------------|
| `MAX_CONTAINERS_PER_HOUR` | Maximum containers per IP address per hour | Yes | 5-10 for CTF events, higher for training |
| `RATE_LIMIT_WINDOW` | Rate limit time window in seconds (typically 3600) | Yes | 3600 (1 hour) is standard |


## 🔧 Creating Custom Challenges

To create a custom challenge:

1. Modify the challenge in `generic_ctf_task/`:
   - Update the `Dockerfile` to build your challenge
   - Ensure your application listens on the port specified in `PORT_IN_CONTAINER`
   - Make sure your application reads the flag from the `FLAG` environment variable (or embed it directly)

2. Update the `.env` file with your challenge details:
   - Set an appropriate title and description
   - Configure the flag (or leave as empty string if embedded)
   - Adjust time and resource settings as needed
   - **Important**: Set a unique `IMAGES_NAME` using the format `localhost/{COMPOSE_PROJECT_NAME}:latest`

3. Rebuild and deploy using the script:
   ```bash
   sudo ./deploy.sh up
   ```

### Example Challenge Structure

```
generic_ctf_task/
├── Dockerfile          # How to build your challenge
└── [challenge files]   # Your challenge files
```

## 🔒 Security Considerations

- Containers run with configurable isolation and resource limits
- User instances are isolated in separate containers
- Rate limiting prevents abuse
- Auto-expiration ensures resources are freed
- Network isolation prevents cross-container interference

## 🔍 Troubleshooting

## ⚠️ Important: Always Use deploy.sh

Always use the `deploy.sh` script to start and stop the deployment. This script performs essential validation and safety checks that help prevent conflicts and errors:

- Validates all required environment variables
- Checks for port conflicts and port range overlaps
- Verifies network configurations
- Ensures unique image names to prevent conflicts between challenges
- Sets up proper locking mechanisms to avoid resource conflicts
- Validates security settings and resource allocations

### Common Issues

#### Image Name Conflicts

If you receive a warning about image name conflicts:

```
[WARNING] Image name conflict detected!
[WARNING] Image localhost/generic_ctf_task:latest is already in use by containers from other projects
```

This means you're trying to use the same image name as another deployment. To fix:

1. Edit your `.env` file
2. Change `IMAGES_NAME` to a unique value: `IMAGES_NAME=localhost/{your_challenge_name}:latest`
3. Restart the deployment with `sudo ./deploy.sh up`

#### Port Range Issues

If you receive errors about port conflicts or no available ports:

1. Check if another deployment is using the same port range
2. Update `START_RANGE` and `STOP_RANGE` to a non-overlapping range
3. Make sure `FLASK_APP_PORT` and `DIRECT_TEST_PORT` are unique

#### Network Conflicts

If you see network errors or conflicts:

1. Ensure `NETWORK_NAME` is unique
2. Set `NETWORK_SUBNET` to a non-overlapping range
3. Restart with `sudo ./deploy.sh down` then `sudo ./deploy.sh up`

### Advanced Debugging

For more detailed diagnostics:

```bash
# View all container logs
docker-compose logs -f

# View just flask_app logs
docker-compose logs -f flask_app

# View logs for a specific challenge container
docker logs [container_id]
```

## 🛠️ Maintenance

### Cleaning Up

The deployment script automatically cleans up stale networks and containers. To manually clean up:

```bash
# Stop all containers and remove networks
sudo ./deploy.sh down

# Remove all unused networks
docker network prune
```

### Updating

```bash
git pull
sudo ./deploy.sh
```

## 📄 License

[MIT License](LICENSE)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
