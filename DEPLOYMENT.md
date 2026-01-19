# HT Status Deployment Guide

This guide covers production deployment of HT Status using Docker Compose or managed cloud services.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Docker Deployment](#docker-deployment)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Deployment Steps](#deployment-steps)
- [Post-Deployment Validation](#post-deployment-validation)
- [Rollback Procedures](#rollback-procedures)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Prerequisites

### System Requirements
- **Python**: 3.9+ with UV package manager installed
- **Docker**: 20.10+ with Docker Compose v2+
- **PostgreSQL**: 13+ (managed service recommended)
- **Redis**: 6+ (managed service recommended)
- **Memory**: Minimum 2GB RAM (4GB+ recommended)
- **Storage**: 10GB+ available disk space

### Access Requirements
- Server SSH access with sudo privileges
- Domain name configured (DNS A record pointing to server)
- SSL certificate (Let's Encrypt recommended)
- Hattrick CHPP API credentials ([register here](https://chpp.hattrick.org/))

### External Services (Recommended)
- **Database**: Managed PostgreSQL (AWS RDS, DigitalOcean, Render)
- **Redis**: Managed Redis (AWS ElastiCache, Redis Cloud)
- **Storage**: S3-compatible object storage for backups
- **Monitoring**: Application performance monitoring (APM) service

---

## Environment Configuration

### 1. Create Production Environment File

Copy and configure production environment variables:

```bash
# Create production .env from template
cp .env.example .env

# Edit with production values
nano .env
```

### 2. Required Production Settings

```bash
# Application Settings
FLASK_ENV=production
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
LOCAL_RUN=false
SECRET_KEY=<generate-strong-random-key-64-chars>

# CHPP API (Production Callback)
CONSUMER_KEY=<your-production-chpp-key>
CONSUMER_SECRETS=<your-production-chpp-secret>
CALLBACK_URL=https://yourdomain.com/login
CHPP_URL=https://chpp.hattrick.org/chppxml.ashx

# Database (Use Managed Service)
DATABASE_URL=postgresql://user:password@managed-db-host:5432/htplanner

# Redis (Use Managed Service)
REDIS_URL=redis://:password@managed-redis-host:6379/0

# Security
DEBUG_LEVEL=0  # No debug output in production
```

### 3. Generate Secure Secret Key

```bash
# Generate 64-character random secret key
python -c 'import secrets; print(secrets.token_hex(32))'
```

### 4. Validate Configuration

```bash
# Validate environment configuration
make config-validate
```

---

## Database Setup

### 1. Use Managed Database Service (Recommended)

**Why Managed Services**:
- Automatic backups and point-in-time recovery
- High availability with automatic failover
- Automated security patches
- Performance monitoring and optimization
- Simplified scaling

**Recommended Providers**:
- AWS RDS PostgreSQL
- DigitalOcean Managed PostgreSQL
- Render PostgreSQL
- Heroku Postgres

### 2. Create Production Database

```sql
-- Connect to PostgreSQL server
CREATE DATABASE htplanner;
CREATE USER htstatus WITH ENCRYPTED PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE htplanner TO htstatus;
```

### 3. Database Migration Procedure

**CRITICAL**: Always backup before migrations

```bash
# 1. Backup current database
pg_dump -h <db-host> -U <db-user> -d htplanner > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Test migration on backup first (restore to test database)
psql -h <db-host> -U <db-user> -d htplanner_test < backup_*.sql

# 3. Run migrations on test database
make db-upgrade

# 4. Verify test database works
make test-integration

# 5. If successful, run on production
make db-upgrade
```

### 4. Database Backup Strategy

```bash
# Automated daily backups (add to cron)
0 2 * * * pg_dump -h <host> -U <user> htplanner | gzip > /backups/htplanner_$(date +\%Y\%m\%d).sql.gz

# Retention policy: Keep 30 days
find /backups -name "htplanner_*.sql.gz" -mtime +30 -delete
```

---

## Docker Deployment

### Option 1: Docker Compose (Small Scale)

**Note**: Docker Compose is suitable for small deployments. For production scale, use managed services.

```bash
# 1. Copy production configuration
cp configs/docker-compose.production.yml docker-compose.override.yml

# 2. Update environment variables in .env

# 3. Start services
docker-compose up -d

# 4. Apply database migrations
docker-compose exec app make db-upgrade

# 5. Verify services
docker-compose ps
```

### Option 2: Managed Services (Recommended)

1. **Deploy Application Container** (AWS ECS, DigitalOcean App Platform, Render)
2. **Configure Database Connection** (use managed PostgreSQL connection string)
3. **Configure Redis** (use managed Redis connection string)
4. **Set Environment Variables** (use platform's secret management)
5. **Run Migrations** (via deployment hook or manual trigger)

---

## Pre-Deployment Checklist

### Code and Configuration
- [ ] All tests passing: `make test-all`
- [ ] Code quality gates passing (linting, security, coverage)
- [ ] Environment variables configured for production
- [ ] Secret keys generated and stored securely
- [ ] CHPP API credentials registered for production domain

### Database
- [ ] Production database created
- [ ] Database user and permissions configured
- [ ] Database connection tested from application server
- [ ] Backup procedure tested and scheduled
- [ ] Migration rollback plan documented

### Infrastructure
- [ ] SSL certificate installed and valid
- [ ] Domain DNS configured correctly
- [ ] Firewall rules configured (allow HTTP/HTTPS only)
- [ ] Server resources adequate (CPU, RAM, disk)
- [ ] Monitoring and alerting configured

### Security
- [ ] Debug mode disabled (`DEBUG_LEVEL=0`)
- [ ] Secret keys rotated from development values
- [ ] Database passwords strong and unique
- [ ] No sensitive data in version control
- [ ] Security headers configured (see TECHNICAL.md)

---

## Deployment Steps

### Initial Deployment

```bash
# 1. Clone repository on production server
git clone <repo-url> /var/www/htstatus
cd /var/www/htstatus

# 2. Checkout specific version
git checkout tags/v1.0.0  # Use specific tag/commit

# 3. Install UV and dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
make setup

# 4. Configure environment
cp .env.example .env
nano .env  # Edit with production values

# 5. Run database migrations
make db-upgrade

# 6. Start application
make dev  # For simple deployment
# OR configure systemd service (see below)
```

### Systemd Service (Recommended)

Create `/etc/systemd/system/htstatus.service`:

```ini
[Unit]
Description=HT Status Application
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/htstatus
Environment="PATH=/var/www/htstatus/.venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/usr/local/bin/uv run python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable htstatus
sudo systemctl start htstatus
sudo systemctl status htstatus
```

### Nginx Reverse Proxy Configuration

Create `/etc/nginx/sites-available/htstatus`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/htstatus /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Subsequent Deployments

```bash
# 1. Backup database
pg_dump -h <host> -U <user> htplanner > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Pull latest code
cd /var/www/htstatus
git fetch origin
git checkout tags/v1.1.0  # New version

# 3. Update dependencies
make update

# 4. Run migrations
make db-upgrade

# 5. Restart application
sudo systemctl restart htstatus

# 6. Verify deployment (see next section)
```

---

## Post-Deployment Validation

### Health Checks

```bash
# 1. Application responds
curl https://yourdomain.com

# 2. Database connection working
curl https://yourdomain.com/health  # If health endpoint exists

# 3. Check application logs
sudo journalctl -u htstatus -n 50 -f

# 4. Verify SSL certificate
curl -I https://yourdomain.com

# 5. Test user authentication
# Login via browser and verify CHPP OAuth flow works
```

### Functional Testing

- [ ] Login with Hattrick account works
- [ ] Team data loads correctly
- [ ] Player information displays
- [ ] Match data accessible
- [ ] Settings save properly

### Performance Checks

```bash
# Response time check
curl -o /dev/null -s -w "Time: %{time_total}s\n" https://yourdomain.com

# Database query performance
# Connect to DB and check slow query log
```

---

## Rollback Procedures

### Emergency Rollback

If deployment fails:

```bash
# 1. Stop application
sudo systemctl stop htstatus

# 2. Rollback code to previous version
cd /var/www/htstatus
git checkout tags/v1.0.0  # Previous working version

# 3. Restore database backup (if migrations ran)
psql -h <host> -U <user> -d htplanner < backup_YYYYMMDD_HHMMSS.sql

# 4. Restart application
sudo systemctl start htstatus

# 5. Verify rollback successful
curl https://yourdomain.com
```

### Migration Rollback

```bash
# Downgrade database one version
make db-downgrade

# Or to specific revision
uv run python -m flask db downgrade <revision_id>
```

---

## Monitoring and Maintenance

### Application Monitoring

- **Logs**: `sudo journalctl -u htstatus -f`
- **Error Tracking**: Configure Sentry or similar APM
- **Uptime Monitoring**: UptimeRobot, Pingdom, or StatusCake
- **Performance**: New Relic, DataDog, or similar

### Database Maintenance

```bash
# Vacuum and analyze (weekly)
psql -h <host> -U <user> -d htplanner -c "VACUUM ANALYZE;"

# Check database size
psql -h <host> -U <user> -d htplanner -c "SELECT pg_size_pretty(pg_database_size('htplanner'));"

# Monitor slow queries
# Enable slow query logging in PostgreSQL configuration
```

### Security Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Python dependencies
make update

# Rebuild and restart
sudo systemctl restart htstatus
```

### Backup Verification

```bash
# Test restore monthly
pg_dump htplanner > test_backup.sql
createdb htplanner_restore_test
psql htplanner_restore_test < test_backup.sql
dropdb htplanner_restore_test
```

---

## Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Check logs
sudo journalctl -u htstatus -n 100

# Verify environment variables
cd /var/www/htstatus
cat .env

# Test configuration
make config-validate
```

**Database connection errors:**
```bash
# Test database connectivity
psql -h <host> -U <user> -d htplanner

# Check if migrations needed
make db-upgrade

# Verify DATABASE_URL in .env
```

**OAuth/Login issues:**
```bash
# Verify CHPP credentials
# Check CALLBACK_URL matches registered URL
# Ensure domain matches production domain
```

### Getting Help

- Review [TECHNICAL.md](TECHNICAL.md) for architecture details
- Check [README.md](README.md) for development setup
- Review logs: `sudo journalctl -u htstatus -f`
- Test locally with production-like config: `make services-staging`

---

## Additional Resources

- **Hattrick CHPP**: https://chpp.hattrick.org/
- **Docker Compose**: https://docs.docker.com/compose/
- **UV Package Manager**: https://docs.astral.sh/uv/
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

**Last Updated**: January 19, 2026
**Maintainer**: HT Status Development Team
