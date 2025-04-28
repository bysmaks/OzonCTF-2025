# 🚀 CTF Challenge Deployer

![Version](https://img.shields.io/badge/version-1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> [ВАЖНО]
> Проверьте .env файл в deploy директории. Нужно убедиться что параматры портов `START_RANGE` `STOP_RANGE` `FLASK_APP_PORT` `DIRECT_TEST_PORT` и параметры сети `NETWORK_SUBNET`
> Не пересекаются с другими портами/подсетями на хостовой операционной системе. При необходимости можно отредактировать эти параметры.
> Задание не будет кореектно работать, если деплоер будет доступен по ссылке с доменного имени, а не IP адреса. 
> Если вы планируете использовать доменное имя при доступе к деплоеру, то необходимо прописать его в snake_game/conf.d/90-decoy.conf 
> пример (90-decoy.conf) line:6 `server_name localhost 127.0.0.1 OZONCTF.RU "" ~^\d+\.\d+\.\d+\.\d+$;`

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
   # Review and modify the .env file as needed
   nano .env
   ```

3. Run the deployment script:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. Access the deployer:
   ```
   http://localhost:6664 (or your configured FLASK_APP_PORT)
   ```

## ⚙️ Configuration

All configuration is done through the `.env` file:

### Key Configuration Options

| Category | Variable | Description |
|----------|----------|-------------|
| **Time** | `LEAVE_TIME` | Container lifetime in seconds |
| | `ADD_TIME` | Extension time in seconds |
| **Ports** | `FLASK_APP_PORT` | Port for the deployer interface |
| | `START_RANGE`/`STOP_RANGE` | Range for dynamic port assignment |
| **Resources** | `CONTAINER_MEMORY_LIMIT` | Memory limit per container |
| | `CONTAINER_CPU_LIMIT` | CPU limit per container |
| **Security** | `ENABLE_NO_NEW_PRIVILEGES` | Prevent privilege escalation |
| | `DROP_ALL_CAPABILITIES` | Drop all container capabilities |

For a complete list with detailed descriptions, see the comments in the `.env` file.

## 🔧 Creating Custom Challenges

To create a custom challenge:

1. Modify the challenge in `generic_ctf_task/`:
   - Update the `Dockerfile` to build your challenge
   - Ensure your application listens on the port specified in `PORT_IN_CONTAINER`
   - Make sure your application reads the flag from the `FLAG` environment variable

2. Update the `.env` file with your challenge details:
   - Set an appropriate title and description
   - Configure the flag
   - Adjust time and resource settings as needed

3. Rebuild and deploy:
   ```bash
   ./deploy.sh
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

### Common Issues

- **No available ports**: The system has reached maximum concurrent containers
- **Rate limit exceeded**: IP has created too many instances
- **Container fails to start**: Check Docker logs for errors
- **Network conflicts**: The deployment script will attempt to find an available subnet

### Logs

```bash
# View deployer logs
docker-compose logs flask_app

# View logs for a specific challenge container
docker logs [container_id]
```

## 🛠️ Maintenance

### Cleaning Up

The deployment script automatically cleans up stale networks and containers. To manually clean up:

```bash
# Stop all containers and remove networks
docker-compose down -v

# Remove all unused networks
docker network prune
```

### Updating

```bash
git pull
./deploy.sh
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
