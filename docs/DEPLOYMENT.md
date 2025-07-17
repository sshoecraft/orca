# Orca Job Orchestrator - Deployment Guide

![Orca Logo](../frontend/public/orca-logo.svg)

Comprehensive deployment guide for production environments.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Application Deployment](#application-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Security Configuration](#security-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Performance Tuning](#performance-tuning)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)

## 🌐 Overview

This guide covers deploying Orca Job Orchestrator in production environments with high availability, security, and performance considerations.

### Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB["🔄 Nginx/HAProxy"]
    end
    
    subgraph "Application Tier"
        API1["🐋 Orca API #1"]
        API2["🐋 Orca API #2"]
        API3["🐋 Orca API #3"]
    end
    
    subgraph "Database Tier"
        DB_PRIMARY[("📊 PostgreSQL Primary")]
        DB_REPLICA[("📊 PostgreSQL Replica")]
    end
    
    subgraph "Monitoring"
        MONITOR["📈 Monitoring Stack"]
        LOGS["📋 Log Aggregation"]
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    API1 --> DB_PRIMARY
    API2 --> DB_PRIMARY
    API3 --> DB_PRIMARY
    DB_PRIMARY --> DB_REPLICA
    API1 --> MONITOR
    API2 --> MONITOR
    API3 --> MONITOR
```

## 🔧 Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 2 vCPUs
- **RAM**: 4 GB
- **Storage**: 20 GB SSD
- **Network**: 100 Mbps

#### Recommended for Production
- **CPU**: 4+ vCPUs
- **RAM**: 8+ GB
- **Storage**: 100+ GB SSD
- **Network**: 1 Gbps

### Software Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql-15 \
    postgresql-client-15 \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    htop \
    ufw

# CentOS/RHEL
sudo dnf install -y \
    python3.11 \
    python3-pip \
    postgresql15-server \
    postgresql15 \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    htop \
    firewalld
```

### Network Configuration

```bash
# Ubuntu/Debian - UFW
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5432/tcp  # PostgreSQL (if remote)
sudo ufw enable

# CentOS/RHEL - firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=5432/tcp
sudo firewall-cmd --reload
```

## 🗄️ Database Setup

### PostgreSQL Installation & Configuration

```bash
# Install PostgreSQL 15
sudo apt install postgresql-15 postgresql-client-15

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Configure PostgreSQL
sudo -u postgres psql
```

```sql
-- Create database and user
CREATE DATABASE orca;
CREATE USER orca_user WITH ENCRYPTED PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE orca TO orca_user;
ALTER USER orca_user CREATEDB;
\q
```

### PostgreSQL Configuration

```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/15/main/postgresql.conf
```

```ini
# /etc/postgresql/15/main/postgresql.conf
listen_addresses = 'localhost'  # Change to '*' for remote access
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'all'
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

```bash
# Edit authentication configuration
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

```ini
# /etc/postgresql/15/main/pg_hba.conf
# Add after existing entries
local   orca            orca_user                               md5
host    orca            orca_user       127.0.0.1/32            md5
host    orca            orca_user       ::1/128                 md5
```

```bash
# Restart PostgreSQL
sudo systemctl restart postgresql

# Test connection
psql -h localhost -U orca_user -d orca
```

### Database Initialization

```bash
# Clone the repository
git clone https://github.com/sshoecraft/orca.git
cd orca

# Initialize database schema
psql -h localhost -U orca_user -d orca -f database/init.sql
```

## 🚀 Application Deployment

### User Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash orca
sudo usermod -aG sudo orca

# Switch to orca user
sudo su - orca
```

### Application Installation

```bash
# Clone repository
git clone https://github.com/sshoecraft/orca.git
cd orca

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### Environment Configuration

```bash
# Edit environment configuration
nano .env
```

```bash
# Production Environment Configuration

# Database Configuration
DATABASE_URL=postgresql://orca_user:secure_password_here@localhost/orca
DATABASE_ECHO=false

# API Configuration
API_TITLE=Orca Job Orchestrator
API_DESCRIPTION=A powerful job orchestrator for multi-system command execution
API_VERSION=1.0.0
DEBUG=false

# Security Configuration
SECRET_KEY=your-very-long-secret-key-here-change-in-production-make-it-64-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-fernet-encryption-key-here

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Job Execution Configuration
MAX_CONCURRENT_JOBS=20
JOB_TIMEOUT_SECONDS=600
CONNECTION_TIMEOUT_SECONDS=30

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Generate Encryption Key

```bash
# Generate Fernet encryption key
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"

# Generate secret key
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"
```

### Systemd Service Configuration

```bash
# Create systemd service file
sudo nano /etc/systemd/system/orca.service
```

```ini
[Unit]
Description=Orca Job Orchestrator
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=orca
Group=orca
WorkingDirectory=/home/orca/orca
Environment=PATH=/home/orca/orca/venv/bin
ExecStart=/home/orca/orca/venv/bin/python run.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/orca/orca

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=orca

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable orca
sudo systemctl start orca

# Check status
sudo systemctl status orca
sudo journalctl -u orca -f
```

## 🌐 Frontend Deployment

### Build Frontend

```bash
# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Build frontend
cd frontend
npm install
npm run build
```

### Nginx Configuration

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/orca
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Frontend static files
    location / {
        root /home/orca/orca/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
    
    # Logging
    access_log /var/log/nginx/orca_access.log;
    error_log /var/log/nginx/orca_error.log;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/orca /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL Certificate

```bash
# Obtain SSL certificate with Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## 🔒 Security Configuration

### Firewall Setup

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Fail2Ban Configuration

```bash
# Install Fail2Ban
sudo apt install fail2ban

# Create Orca jail
sudo nano /etc/fail2ban/jail.d/orca.conf
```

```ini
[orca-auth]
enabled = true
port = http,https
filter = orca-auth
logpath = /var/log/nginx/orca_access.log
maxretry = 5
bantime = 3600
findtime = 600
```

```bash
# Create filter
sudo nano /etc/fail2ban/filter.d/orca-auth.conf
```

```ini
[Definition]
failregex = ^<HOST> .* "POST /api/auth/token HTTP/.*" 401 .*$
ignoreregex =
```

```bash
# Restart Fail2Ban
sudo systemctl restart fail2ban
```

### Security Hardening

```bash
# Disable root login
sudo passwd -l root

# Configure SSH
sudo nano /etc/ssh/sshd_config
```

```bash
# SSH Security Configuration
Port 22
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthenticationMethods publickey
ClientAliveInterval 300
ClientAliveCountMax 2
MaxAuthTries 3
MaxSessions 10
```

```bash
# Restart SSH
sudo systemctl restart ssh
```

## 📊 Monitoring & Logging

### Log Rotation

```bash
# Configure log rotation
sudo nano /etc/logrotate.d/orca
```

```bash
/var/log/nginx/orca_*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 `cat /var/run/nginx.pid`
        fi
    endscript
}
```

### Health Monitoring Script

```bash
# Create monitoring script
nano /home/orca/monitor.sh
```

```bash
#!/bin/bash

# Orca Health Monitor
LOG_FILE="/var/log/orca_monitor.log"
API_URL="http://localhost:8000/health"

echo "$(date): Checking Orca health..." >> $LOG_FILE

# Check API health
if curl -f -s $API_URL > /dev/null; then
    echo "$(date): API is healthy" >> $LOG_FILE
else
    echo "$(date): API is down! Restarting service..." >> $LOG_FILE
    sudo systemctl restart orca
    
    # Send alert (configure email/Slack webhook)
    # curl -X POST -H 'Content-type: application/json' \
    #   --data '{"text":"Orca API is down and was restarted"}' \
    #   YOUR_SLACK_WEBHOOK_URL
fi

# Check database connectivity
if sudo -u orca psql -h localhost -U orca_user -d orca -c "SELECT 1;" > /dev/null 2>&1; then
    echo "$(date): Database is healthy" >> $LOG_FILE
else
    echo "$(date): Database connection failed!" >> $LOG_FILE
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Warning: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi
```

```bash
# Make executable and add to cron
chmod +x /home/orca/monitor.sh

# Add to crontab
crontab -e
```

```bash
# Run health check every 5 minutes
*/5 * * * * /home/orca/monitor.sh
```

## ⚡ Performance Tuning

### Database Optimization

```sql
-- Create additional indexes for performance
CREATE INDEX CONCURRENTLY idx_job_executions_created_at ON job_executions(started_at DESC);
CREATE INDEX CONCURRENTLY idx_systems_hostname ON systems(hostname);
CREATE INDEX CONCURRENTLY idx_audit_logs_user_action ON audit_logs(user_id, action);

-- Update table statistics
ANALYZE;
```

### Nginx Optimization

```nginx
# Add to nginx.conf
worker_processes auto;
worker_connections 1024;

# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/javascript
    application/xml+rss
    application/json;

# Connection optimization
keepalive_timeout 65;
keepalive_requests 100;

# Buffer sizes
client_body_buffer_size 128k;
client_max_body_size 10m;
client_header_buffer_size 1k;
large_client_header_buffers 4 4k;
```

### Application Optimization

```bash
# Add to .env for production
MAX_CONCURRENT_JOBS=50
JOB_TIMEOUT_SECONDS=300
CONNECTION_TIMEOUT_SECONDS=30
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

## 💾 Backup & Recovery

### Database Backup

```bash
# Create backup script
nano /home/orca/backup.sh
```

```bash
#!/bin/bash

BACKUP_DIR="/home/orca/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="orca_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -h localhost -U orca_user -d orca > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

```bash
# Make executable and schedule
chmod +x /home/orca/backup.sh

# Add to crontab for daily backups at 2 AM
crontab -e
```

```bash
0 2 * * * /home/orca/backup.sh
```

### Disaster Recovery

```bash
# Restore from backup
gunzip orca_backup_20250117_020000.sql.gz
psql -h localhost -U orca_user -d orca < orca_backup_20250117_020000.sql
```

## 🔍 Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check service status
sudo systemctl status orca

# Check logs
sudo journalctl -u orca -f

# Check environment
sudo -u orca bash -c 'cd /home/orca/orca && source venv/bin/activate && python -c "from backend.core.config import settings; print(settings.database_url)"'
```

#### Database Connection Issues

```bash
# Test database connection
sudo -u orca psql -h localhost -U orca_user -d orca

# Check PostgreSQL status
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

#### High Memory Usage

```bash
# Check memory usage
ps aux | grep python
free -h

# Restart service
sudo systemctl restart orca
```

### Maintenance Commands

```bash
# Update application
sudo su - orca
cd orca
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart orca

# Check application health
curl http://localhost:8000/health

# View recent logs
sudo journalctl -u orca --since "1 hour ago"

# Database maintenance
sudo -u postgres psql -d orca -c "VACUUM ANALYZE;"
```

---

🐋 **Orca Job Orchestrator** - Production-ready deployment completed!