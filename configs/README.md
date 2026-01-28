# Configuration Files

**Docker Environments**: Use `make services-dev` or `make services-staging`
**Tool Configs**: Linting, formatting, and deployment settings

## Notes

- Most configurations have been migrated to modern equivalents (pyproject.toml, ruff, etc.)
- Legacy files are maintained for backward compatibility
- Docker Compose files provide environment-specific service configurations
- Production environments should use managed services instead of Docker Compose
