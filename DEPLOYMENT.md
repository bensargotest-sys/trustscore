# TrustScore Deployment Guide

This guide covers deploying TrustScore in various environments, from local development to production.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production (VPS/Cloud)](#production-vpscloud)
4. [Integration with AI Agents](#integration-with-ai-agents)
5. [Configuration](#configuration)
6. [Monitoring](#monitoring)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)

---

## Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/bensargotest-sys/trustscore.git
cd trustscore

# Install dependencies
npm install

# Build TypeScript
npm run build

# Run in development mode
npm run dev

# Run tests
npm test
```

### Development Server

Development server runs on `stdio` transport (local only):

```bash
npm run dev
# Server starts, communicates via stdin/stdout
# Connect using MCP client examples in examples/
```

### Database Location

- **Development:** `./trustscore.db` (SQLite)
- **Tests:** `./test.db` (auto-created, auto-cleaned)

---

## Docker Deployment

### Build Image

```bash
# Build Docker image
docker build -t trustscore:latest .

# Or use docker-compose
docker-compose build
```

### Run Container

```bash
# Run with default config
docker run -d \
  --name trustscore \
  -v $(pwd)/data:/app/data \
  trustscore:latest

# Run with custom port (HTTP transport)
docker run -d \
  --name trustscore \
  -p 3000:3000 \
  -v $(pwd)/data:/app/data \
  -e TRANSPORT=http \
  -e PORT=3000 \
  trustscore:latest
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  trustscore:
    build: .
    container_name: trustscore
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - NODE_ENV=production
      - TRANSPORT=http
      - PORT=3000
      - DB_PATH=/app/data/trustscore.db
    healthcheck:
      test: ["CMD", "node", "healthcheck.js"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose up -d
```

---

## Production (VPS/Cloud)

### System Requirements

**Minimum:**
- 1 CPU core
- 512MB RAM
- 10GB disk
- Node.js 18+

**Recommended:**
- 2 CPU cores
- 2GB RAM
- 50GB disk (for logs + historical data)
- Node.js 20+

### Installation (Ubuntu/Debian)

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create app directory
sudo mkdir -p /opt/trustscore
cd /opt/trustscore

# Clone repository
sudo git clone https://github.com/bensargotest-sys/trustscore.git .

# Install dependencies
sudo npm install --production

# Build
sudo npm run build

# Set permissions
sudo chown -R trustscore:trustscore /opt/trustscore
```

### Create Service User

```bash
# Create dedicated user
sudo useradd -r -s /bin/false trustscore

# Set ownership
sudo chown -R trustscore:trustscore /opt/trustscore
```

### Systemd Service

Create `/etc/systemd/system/trustscore.service`:

```ini
[Unit]
Description=TrustScore MCP Server
After=network.target

[Service]
Type=simple
User=trustscore
Group=trustscore
WorkingDirectory=/opt/trustscore
ExecStart=/usr/bin/node /opt/trustscore/dist/index.js
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=trustscore

# Environment
Environment=NODE_ENV=production
Environment=TRANSPORT=http
Environment=PORT=3000
Environment=DB_PATH=/opt/trustscore/data/trustscore.db

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/trustscore/data /opt/trustscore/logs

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable trustscore
sudo systemctl start trustscore
sudo systemctl status trustscore
```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/trustscore
server {
    listen 80;
    server_name trustscore.example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/trustscore /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL with Let's Encrypt

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d trustscore.example.com

# Auto-renewal (cron)
sudo certbot renew --dry-run
```

---

## Integration with AI Agents

### LangGraph (HTTP Transport)

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "trustscore": {
        "transport": "http",
        "url": "https://trustscore.example.com/mcp",
        "headers": {
            "Authorization": "Bearer your_token"  # Optional
        }
    }
})
```

### CrewAI (HTTP Transport)

```python
from crewai.mcp import MCPServerHTTP

mcps=[
    MCPServerHTTP(
        url="https://trustscore.example.com/mcp",
        headers={"Authorization": "Bearer your_token"},
        streamable=True,
    )
]
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "trustscore": {
      "transport": "http",
      "url": "https://trustscore.example.com/mcp"
    }
  }
}
```

---

## Configuration

### Environment Variables

```bash
# Server
NODE_ENV=production          # production | development
TRANSPORT=http               # stdio | http | sse
PORT=3000                    # HTTP server port

# Database
DB_PATH=/opt/trustscore/data/trustscore.db
DB_POOL_SIZE=10             # Connection pool size

# Logging
LOG_LEVEL=info              # debug | info | warn | error
LOG_PATH=/opt/trustscore/logs

# Performance
CACHE_TTL=300               # Cache TTL in seconds
MAX_CONNECTIONS=100         # Max concurrent connections

# Security
API_KEY=your_secret_key     # Optional: API authentication
CORS_ORIGIN=*               # CORS allowed origins
RATE_LIMIT=100              # Requests per minute per IP
```

### Config File

Create `config/production.json`:

```json
{
  "server": {
    "transport": "http",
    "port": 3000,
    "host": "0.0.0.0"
  },
  "database": {
    "path": "/opt/trustscore/data/trustscore.db",
    "poolSize": 10,
    "timeout": 5000
  },
  "scoring": {
    "dimensions": {
      "reliability": 0.25,
      "uptime": 0.20,
      "latency": 0.15,
      "errorRate": 0.15,
      "quality": 0.10,
      "dataFreshness": 0.10,
      "security": 0.05
    },
    "confidenceThresholds": {
      "low": 20,
      "medium": 100
    }
  },
  "cache": {
    "enabled": true,
    "ttl": 300
  },
  "security": {
    "apiKey": "${API_KEY}",
    "corsOrigin": "*",
    "rateLimit": 100
  }
}
```

---

## Monitoring

### Health Check Endpoint

```bash
# Check server health
curl http://localhost:3000/health

# Expected response:
{
  "status": "healthy",
  "uptime": 3600,
  "database": "connected",
  "version": "0.1.0"
}
```

### Prometheus Metrics

Enable metrics in `config.json`:

```json
{
  "metrics": {
    "enabled": true,
    "port": 9090
  }
}
```

Scrape config:
```yaml
scrape_configs:
  - job_name: 'trustscore'
    static_configs:
      - targets: ['localhost:9090']
```

### Logs

View logs:
```bash
# Systemd logs
sudo journalctl -u trustscore -f

# File logs
tail -f /opt/trustscore/logs/trustscore.log
```

Log rotation (logrotate):
```
/opt/trustscore/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 trustscore trustscore
    sharedscripts
    postrotate
        systemctl reload trustscore > /dev/null 2>&1 || true
    endscript
}
```

---

## Backup & Recovery

### Database Backup

```bash
# Manual backup
sqlite3 /opt/trustscore/data/trustscore.db ".backup /opt/trustscore/backups/backup-$(date +%Y%m%d).db"

# Automated backup (cron)
0 2 * * * sqlite3 /opt/trustscore/data/trustscore.db ".backup /opt/trustscore/backups/backup-$(date +\%Y\%m\%d).db"
```

### Backup Script

```bash
#!/bin/bash
# /opt/trustscore/scripts/backup.sh

BACKUP_DIR="/opt/trustscore/backups"
DB_PATH="/opt/trustscore/data/trustscore.db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/trustscore-$DATE.db"

# Create backup
sqlite3 "$DB_PATH" ".backup $BACKUP_FILE"

# Compress
gzip "$BACKUP_FILE"

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "*.db.gz" -mtime +30 -delete

echo "Backup complete: $BACKUP_FILE.gz"
```

### Restore from Backup

```bash
# Stop service
sudo systemctl stop trustscore

# Restore database
gunzip -c /opt/trustscore/backups/trustscore-20260211.db.gz > /opt/trustscore/data/trustscore.db

# Set permissions
sudo chown trustscore:trustscore /opt/trustscore/data/trustscore.db

# Start service
sudo systemctl start trustscore
```

---

## Troubleshooting

### Server Won't Start

**Check logs:**
```bash
sudo journalctl -u trustscore -n 50
```

**Common issues:**
- Port already in use: Change PORT env var
- Permission denied: Check file ownership
- Database locked: Check for stale connections

### High Memory Usage

**Check stats:**
```bash
# Process stats
ps aux | grep node

# Memory usage
free -h
```

**Solutions:**
- Reduce `DB_POOL_SIZE`
- Enable caching with lower `CACHE_TTL`
- Restart service periodically

### Slow Queries

**Enable query logging:**
```json
{
  "database": {
    "logQueries": true,
    "slowQueryThreshold": 1000
  }
}
```

**Solutions:**
- Add indexes (see `schema.sql`)
- Archive old data
- Increase `DB_POOL_SIZE`

### Connection Timeouts

**Increase timeouts:**
```json
{
  "database": {
    "timeout": 10000
  },
  "server": {
    "requestTimeout": 30000
  }
}
```

---

## Security Checklist

- [ ] Enable API key authentication
- [ ] Use HTTPS in production
- [ ] Configure firewall (allow only necessary ports)
- [ ] Set strong file permissions (600 for DB, 640 for logs)
- [ ] Enable rate limiting
- [ ] Regular security updates (`npm audit`)
- [ ] Backup database regularly
- [ ] Monitor logs for suspicious activity
- [ ] Use non-root user for service
- [ ] Enable systemd security features

---

## Performance Tuning

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_interactions_provider 
  ON interactions(provider_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_interactions_success 
  ON interactions(success, timestamp);

-- Enable WAL mode for better concurrency
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
```

### Caching Strategy

```json
{
  "cache": {
    "enabled": true,
    "ttl": 300,              // Cache for 5 minutes
    "maxSize": 1000,         // Max 1000 entries
    "strategy": "lru"        // Least Recently Used
  }
}
```

### Connection Pooling

```json
{
  "database": {
    "poolSize": 10,          // Number of connections
    "acquireTimeout": 5000,  // Wait 5s for connection
    "idleTimeout": 30000     // Close idle after 30s
  }
}
```

---

## Scaling

### Horizontal Scaling

For high-traffic deployments:

1. **Load Balancer:** Nginx/HAProxy in front of multiple TrustScore instances
2. **Shared Database:** Use PostgreSQL instead of SQLite
3. **Redis Cache:** Shared cache across instances
4. **Session Affinity:** Sticky sessions for consistency

### Vertical Scaling

For single-instance deployments:

1. **Increase Resources:** More CPU/RAM
2. **Optimize Queries:** Add indexes, cache aggressively
3. **Archive Old Data:** Move historical data to cold storage

---

## Next Steps

1. **Deploy to staging:** Test in non-production environment
2. **Load testing:** Use `artillery` or `k6` to test under load
3. **Monitor metrics:** Set up Prometheus + Grafana
4. **Automate backups:** Schedule daily backups
5. **Document runbooks:** Create incident response procedures

---

**Questions?** Open an issue on GitHub or join the MCP Discord.
