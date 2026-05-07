# Docker Container Conflict Troubleshooting

## 🚨 Common Error: Container Name Already in Use

```
Error response from daemon: Conflict. The container name "/selenium-hub" is already in use
```

## 🔧 Root Causes

1. **Previous Jenkins job didn't clean up properly**
2. **Docker containers in orphaned state**
3. **Network conflicts**
4. **Docker daemon issues**

## 🛠️ Immediate Solutions

### Solution 1: Manual Cleanup (Recommended)
```bash
# Stop all Selenium containers
docker stop selenium-hub chrome-node-1 chrome-node-2 chrome-node-3 chrome-node-4 firefox-node-1 firefox-node-2

# Remove all Selenium containers
docker rm selenium-hub chrome-node-1 chrome-node-2 chrome-node-3 chrome-node-4 firefox-node-1 firefox-node-2

# Clean up networks
docker network prune -f

# Restart Docker service (if needed)
# Windows: Restart Docker Desktop
# Linux: sudo systemctl restart docker
```

### Solution 2: Force Cleanup
```bash
# Remove all containers (force)
docker rm -f $(docker ps -aq)

# Remove all networks
docker network prune -f

# Clean up Docker system
docker system prune -f
```

### Solution 3: Docker Compose Reset
```bash
# Force down with cleanup
docker-compose down -v --remove-orphans

# Remove project-specific containers
docker-compose rm -f

# Start fresh
docker-compose up -d
```

## 🔍 Jenkins File Improvements

The updated Jenkinsfile now includes robust cleanup:

### Enhanced Cleanup Commands (Windows Jenkins Compatible)
```bash
# Force stop and remove all containers including orphaned ones
docker compose down -v --remove-orphans
docker stop selenium-hub chrome-node-1 chrome-node-2 chrome-node-3 chrome-node-4 firefox-node-1 firefox-node-2
docker rm selenium-hub chrome-node-1 chrome-node-2 chrome-node-3 chrome-node-4 firefox-node-1 firefox-node-2
docker network prune -f
```

### Jenkins-Specific Fixes
- **Replaced**: `timeout /t 30 /nobreak` → `ping 127.0.0.1 -n 31 > nul`
- **Replaced**: `|| true` → No error suppression (proper Windows batch syntax)
- **Updated**: `docker-compose` → `docker compose` (modern Docker syntax)

### Error Diagnostics
```bash
# Display current status for debugging
docker ps -a
docker-compose ps
docker network ls
```

## 🚀 Prevention Strategies

### 1. Proper Container Naming
- Use consistent naming conventions
- Include project prefixes to avoid conflicts

### 2. Graceful Shutdown
- Always use `docker-compose down` before system restart
- Implement proper cleanup in CI/CD pipelines

### 3. Resource Monitoring
```bash
# Monitor container status
docker stats

# Check resource usage
docker system df

# View logs for issues
docker logs selenium-hub
```

## 🔧 Environment-Specific Fixes

### Windows/Docker Desktop
```cmd
# Restart Docker Desktop
# Right-click Docker Desktop icon > Restart

# Clear Docker cache
# Docker Desktop > Settings > Resources > File Sharing > Reset
```

### Linux
```bash
# Restart Docker service
sudo systemctl restart docker

# Clean up Docker resources
sudo docker system prune -a
```

### Jenkins Environment
```bash
# Run as Jenkins user (if needed)
sudo -u jenkins docker-compose down -v

# Check Docker permissions
sudo usermod -aG docker jenkins
```

## 📊 Diagnostic Commands

### Container Status
```bash
# List all containers
docker ps -a

# Filter Selenium containers
docker ps -a --filter "name=selenium"

# Show container details
docker inspect selenium-hub
```

### Network Issues
```bash
# List networks
docker network ls

# Show network details
docker network inspect bridge
```

### Resource Usage
```bash
# Disk usage
docker system df

# Detailed system info
docker system info
```

## 🎯 Best Practices

### 1. Always Clean Up
```bash
# In scripts, always include cleanup
trap 'docker-compose down -v' EXIT
```

### 2. Use Health Checks
```bash
# Verify containers are running
docker ps --filter "status=running"
```

### 3. Monitor Logs
```bash
# Follow logs in real-time
docker-compose logs -f
```

### 4. Version Management
```bash
# Use specific image versions
image: selenium/hub:4.21.0
```

## 🆘 Emergency Recovery

### Complete Docker Reset
```bash
# WARNING: This removes ALL Docker data
# Stop Docker service
sudo systemctl stop docker

# Remove Docker data directory
sudo rm -rf /var/lib/docker

# Restart Docker
sudo systemctl start docker
```

### Jenkins-Specific Recovery
```bash
# Clear Jenkins workspace
rm -rf /var/lib/jenkins/workspace/*

# Restart Jenkins
sudo systemctl restart jenkins
```

## 📞 Support Commands for Jenkins

When the Jenkins job fails, run these commands to diagnose:

```bash
# Check what's running
docker ps -a

# Check Jenkins workspace
ls -la /var/lib/jenkins/workspace/your-job-name/

# Manual test
cd /var/lib/jenkins/workspace/your-job-name/
docker-compose up -d
```

This should resolve the container conflict issues and provide robust cleanup for future runs.
