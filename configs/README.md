# Configuration Files Directory

This directory contains configuration files for various tools and deployment environments.

## Docker Compose Configurations

Environment-specific Docker Compose override files:

- **`docker-compose.development.yml`** - Development with pgAdmin and sample data
- **`docker-compose.staging.yml`** - Staging with resource limits and monitoring  
- **`docker-compose.production.yml`** - Production reference (use managed services instead)

### Usage

```bash
# Development
docker-compose -f docker-compose.yml -f configs/docker-compose.development.yml up -d

# Staging  
docker-compose -f docker-compose.yml -f configs/docker-compose.staging.yml up -d

# Or use Makefile commands
make services-dev     # Development services
make services-staging # Staging services
```

## Tool Configurations

- **`.flake8`** - Flake8 linter configuration (legacy, now using ruff)
- **`index.html`** - Static HTML template/placeholder
- **`requirements.txt`** - Legacy Python requirements (now using pyproject.toml + UV)

## Notes

- Most configurations have been migrated to modern equivalents (pyproject.toml, ruff, etc.)
- Legacy files are maintained for backward compatibility
- Docker Compose files provide environment-specific service configurations
- Production environments should use managed services instead of Docker Compose