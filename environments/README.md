# Environment Templates Directory

This directory contains environment configuration templates for different deployment scenarios.

## Environment Templates

- **`.env.development.example`** - Development environment with helpful defaults
- **`.env.staging.example`** - Staging environment with security enhancements
- **`.env.production.example`** - Production environment with strict security requirements
- **`config.py.example`** - Legacy configuration file template

## Usage

Choose the appropriate template for your environment:

### Development Setup
```bash
cp environments/.env.development.example .env
# Edit .env with your CHPP API credentials
nano .env
```

### Staging Setup
```bash
cp environments/.env.staging.example .env
# Configure staging-specific values
nano .env
```

### Production Setup
```bash
cp environments/.env.production.example .env
# IMPORTANT: Replace ALL placeholder values with secure production values
nano .env
```

## Configuration Validation

After setting up your environment, validate the configuration:

```bash
make config-validate
```

## Security Notes

- **Never commit actual `.env` files** - only the `.example` templates
- **Production template requires ALL placeholders to be replaced**
- **Use strong secrets for production environments**
- **Enable SSL/TLS for production databases and Redis**

See the main README.md for detailed configuration instructions.
