# OpenMaps Auth - Docker Build Guide

## Overview

This document describes the Docker-based build and deployment architecture for openmaps-auth. This service provides authentication for OpenMaps using login.gov and integrates with MapEdit's session management.

## Architecture

### Container Architecture
```
┌─────────────────────────────────────────┐
│ Container (Port 8080)                   │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Gunicorn WSGI Server             │  │
│  │ - Workers: 4                     │  │
│  │ - Threads: 2                     │  │
│  │ - Bind: 0.0.0.0:8080             │  │
│  └──────────────────────────────────┘  │
│                ↓                        │
│  ┌──────────────────────────────────┐  │
│  │ Flask Application                │  │
│  │ - Login.gov OAuth integration    │  │
│  │ - Session management             │  │
│  │ - Token refresh                  │  │
│  └──────────────────────────────────┘  │
│                ↓                        │
│  ┌──────────────────────────────────┐  │
│  │ PostgreSQL Database              │  │
│  │ - User sessions                  │  │
│  │ - OAuth tokens                   │  │
│  └──────────────────────────────────┘  │
│                                         │
│  Built from: Dockerfile                 │
│  Base: python:3.10-slim                 │
└─────────────────────────────────────────┘
```

## Dockerfile Structure

### Base Image
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*
```

**Why Python 3.10:**
- Stable, well-supported version
- Compatible with all dependencies
- Security updates available
- Slim variant reduces image size

### Application Setup
```dockerfile
# Create app directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -r -u 999 -g 999 auth && \
    chown -R auth:auth /app

USER auth:auth

# Expose port
EXPOSE 8080

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--threads", "2", "app:app"]
```

## Key Components

### 1. Dependencies (`requirements.txt`)

**Core Dependencies:**
```txt
Flask==2.3.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
requests==2.31.0
python-jose[cryptography]==3.3.0
```

**Authentication:**
```txt
authlib==1.2.1
```

**Database:**
```txt
SQLAlchemy==2.0.23
alembic==1.13.0
```

### 2. Configuration

**Environment Variables:**
```bash
# Database
POSTGRES_HOST=openmaps-postgres
POSTGRES_PORT=5432
POSTGRES_DB=auth
POSTGRES_USER=auth
POSTGRES_PASSWORD=<secret>

# Login.gov OAuth
LOGINGOV_CLIENT_ID=<client-id>
LOGINGOV_PRIVATE_KEY=<private-key>
LOGINGOV_REDIRECT_URI=https://dev.fm-maxarmaps.com/auth/callback
LOGINGOV_ISSUER=https://idp.int.identitysandbox.gov

# Application
FLASK_ENV=production
SECRET_KEY=<secret>
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

**Kubernetes ConfigMap:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: auth
data:
  POSTGRES_HOST: openmaps-postgres
  POSTGRES_PORT: "5432"
  POSTGRES_DB: auth
  LOGINGOV_REDIRECT_URI: https://dev.fm-maxarmaps.com/auth/callback
  LOGINGOV_ISSUER: https://idp.int.identitysandbox.gov
```

**Kubernetes Secret:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: auth
type: Opaque
stringData:
  POSTGRES_PASSWORD: <secret>
  LOGINGOV_CLIENT_ID: <client-id>
  LOGINGOV_PRIVATE_KEY: |
    -----BEGIN PRIVATE KEY-----
    ...
    -----END PRIVATE KEY-----
  SECRET_KEY: <secret>
```

### 3. Database Schema

**Tables:**
```sql
-- User sessions
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

-- OAuth tokens
CREATE TABLE oauth_tokens (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Migrations:**
```bash
# Run migrations in init container
alembic upgrade head
```

## Build Process

### 1. Local Build
```bash
cd openmaps-auth
docker build -t openmaps-auth:local .
```

### 2. ECR Build & Push
```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  664418996761.dkr.ecr.us-east-1.amazonaws.com

# Build with version tag
VERSION=0.8.14
docker build \
  -t 664418996761.dkr.ecr.us-east-1.amazonaws.com/openmaps/auth:${VERSION} .

# Push to ECR
docker push 664418996761.dkr.ecr.us-east-1.amazonaws.com/openmaps/auth:${VERSION}
```

### 3. Version Tagging
- Use semantic versioning: `MAJOR.MINOR.PATCH`
- Example: `0.8.14`
- Increment PATCH for bug fixes
- Increment MINOR for new features
- Increment MAJOR for breaking changes

## Deployment

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth
spec:
  replicas: 2
  selector:
    matchLabels:
      app: auth
  template:
    metadata:
      labels:
        app: auth
    spec:
      initContainers:
      - name: wait-for-postgres
        image: postgres:15
        command: ['sh', '-c', 'until pg_isready -h openmaps-postgres -p 5432; do sleep 2; done']
      
      - name: run-migrations
        image: 664418996761.dkr.ecr.us-east-1.amazonaws.com/openmaps/auth:0.8.14
        command: ['alembic', 'upgrade', 'head']
        envFrom:
        - configMapRef:
            name: auth
        - secretRef:
            name: auth
      
      containers:
      - name: auth
        image: 664418996761.dkr.ecr.us-east-1.amazonaws.com/openmaps/auth:0.8.14
        ports:
        - containerPort: 8080
          name: http
        envFrom:
        - configMapRef:
            name: auth
        - secretRef:
            name: auth
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: auth
spec:
  selector:
    app: auth
  ports:
  - port: 80
    targetPort: 8080
    name: http
```

## Integration with MapEdit

### Authentication Flow

1. **User visits MapEdit** → Redirected to `/auth/login`
2. **Auth service** → Redirects to login.gov
3. **User authenticates** → login.gov redirects to `/auth/callback`
4. **Auth service** → Creates session, redirects to MapEdit
5. **MapEdit** → Validates session with auth service

### Session Validation
```python
# MapEdit validates session via auth service
GET /auth/validate?session_id=<session-id>

# Response:
{
  "valid": true,
  "user_id": "12345",
  "email": "user@example.com",
  "expires_at": "2025-11-18T18:00:00Z"
}
```

### Token Refresh
```python
# Auth service automatically refreshes OAuth tokens
# Background job runs every 30 minutes
# Refreshes tokens expiring within 1 hour
```

## Health Checks

### Endpoint: `/health`
```python
@app.route('/health')
def health():
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        return {'status': 'healthy'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503
```

## Security

### Non-Root Execution
```dockerfile
USER auth:auth
```

### Secrets Management
- All secrets stored in Kubernetes Secrets
- Never committed to git
- Rotated regularly

### HTTPS Only
```python
SESSION_COOKIE_SECURE=true  # Only send over HTTPS
SESSION_COOKIE_HTTPONLY=true  # Prevent XSS
SESSION_COOKIE_SAMESITE=Lax  # CSRF protection
```

## Troubleshooting

### Common Issues

**1. Database Connection Failures**
```bash
# Check if postgres is ready
kubectl exec -it auth-pod -- pg_isready -h openmaps-postgres -p 5432

# Check environment variables
kubectl exec -it auth-pod -- env | grep POSTGRES
```

**2. Login.gov OAuth Errors**
```bash
# Verify private key is correctly formatted
kubectl get secret auth -o jsonpath='{.data.LOGINGOV_PRIVATE_KEY}' | base64 -d

# Check redirect URI matches login.gov configuration
kubectl get configmap auth -o jsonpath='{.data.LOGINGOV_REDIRECT_URI}'
```

**3. Session Validation Failures**
```bash
# Check session table
kubectl exec -it openmaps-postgres-pod -- psql -U auth -d auth -c "SELECT * FROM sessions LIMIT 10;"

# Check auth service logs
kubectl logs -f auth-pod
```

## Monitoring

### Metrics
- Request rate
- Response time
- Error rate
- Active sessions
- Token refresh success rate

### Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Related Documentation

- [openmaps: Helm Chart Migration](../../openmaps/docs/DOCKERFILE_MODERN_MIGRATION.md)
- [mapedit-osm: Dockerfile.modern Architecture](../../mapedit-osm/docs/DOCKERFILE_MODERN_ARCHITECTURE.md)
- [README](../README.md)

## Future Enhancements

- [ ] Add metrics endpoint
- [ ] Implement distributed tracing
- [ ] Add rate limiting
- [ ] Support additional OAuth providers
- [ ] Implement session cleanup job

