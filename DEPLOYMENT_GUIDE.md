# Aegis Orchestrator - Deployment Guide

**Author:** Hasibur Rashid  
**Email:** atm.hasibur.rashid20367@gmail.com

## Quick Start

### 1. Prerequisites
- Python 3.8+
- Docker
- Kubernetes cluster (GKE recommended)
- Google Cloud SDK
- kubectl

### 2. Local Development
```bash
# Clone repository
git clone <repository-url>
cd aegis-orchestrator

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp config/env.example .env
# Edit .env with your API keys

# Run web demo
python web_demo_simple.py
# Open http://localhost:8000

# Run automatic demo
python auto_demo.py
```

### 3. Production Deployment

#### Step 1: Configure Secrets
```bash
# Create Kubernetes secret
kubectl create secret generic aegis-secrets \
  --from-literal=GEMINI_API_KEY="your_api_key_here" \
  --from-literal=GEMINI_MODEL="gemini-1.5-pro" \
  -n aegis-orchestrator
```

#### Step 2: Deploy to GKE
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy all components
kubectl apply -f k8s/

# Check status
kubectl get pods -n aegis-orchestrator
```

#### Step 3: Verify Deployment
```bash
# Check all services
kubectl get services -n aegis-orchestrator

# Check logs
kubectl logs -f deployment/orchestrator-agent -n aegis-orchestrator
```

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Online        │    │   Aegis         │    │   Google        │
│   Boutique      │◄──►│   Orchestrator  │◄──►│   Gemini AI     │
│   (External)    │    │   (This App)    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Kubernetes    │
                       │   Cluster       │
                       └─────────────────┘
```

## Components

### 1. MCP Server
- **Purpose:** Safe gateway between AI agents and Online Boutique
- **Port:** 8001
- **Protocol:** Model Context Protocol

### 2. AI Agents
- **Orchestrator Agent:** Central decision maker
- **Personalization Agent:** Customer recommendations
- **Inventory Agent:** Stock management
- **Customer Comms Agent:** Proactive communication
- **Anomaly Resolver Agent:** Problem resolution

### 3. Web Interface
- **Purpose:** Interactive demonstration
- **Port:** 8000
- **Features:** Real-time monitoring, customer simulation

## Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-pro
API_HOST=0.0.0.0
API_PORT=8000
BOUTIQUE_BASE_URL=http://online-boutique:8080
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001
REDIS_URL=redis://redis:6379
```

### Kubernetes Configuration
- **Namespace:** aegis-orchestrator
- **Resources:** CPU/Memory limits defined
- **Health Checks:** Liveness and readiness probes
- **Scaling:** Horizontal Pod Autoscaler ready

## Monitoring

### 1. Health Checks
```bash
# Check pod health
kubectl get pods -n aegis-orchestrator

# Check service endpoints
kubectl get endpoints -n aegis-orchestrator
```

### 2. Logs
```bash
# View all logs
kubectl logs -f deployment/orchestrator-agent -n aegis-orchestrator

# View specific agent logs
kubectl logs -f deployment/personalization-agent -n aegis-orchestrator
```

### 3. Metrics
- **AI Decisions:** Real-time AI decision count
- **Events Processed:** System event throughput
- **Problems Resolved:** Anomaly resolution rate
- **Customer Interactions:** Communication volume

## Troubleshooting

### Common Issues

#### 1. API Key Not Found
```bash
# Check secret exists
kubectl get secret aegis-secrets -n aegis-orchestrator

# Verify secret content
kubectl get secret aegis-secrets -n aegis-orchestrator -o yaml
```

#### 2. Pod Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n aegis-orchestrator

# Check events
kubectl get events -n aegis-orchestrator
```

#### 3. Service Not Accessible
```bash
# Check service
kubectl get service <service-name> -n aegis-orchestrator

# Check endpoints
kubectl get endpoints <service-name> -n aegis-orchestrator
```

## Security

### 1. API Key Management
- Use Kubernetes secrets
- Rotate keys regularly
- Monitor key usage

### 2. Network Security
- Implement network policies
- Use TLS for communication
- Restrict pod-to-pod communication

### 3. Access Control
- Use RBAC for Kubernetes
- Implement API authentication
- Monitor access logs

## Performance Optimization

### 1. Resource Allocation
```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### 2. Scaling
```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: orchestrator-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: orchestrator-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 3. Caching
- Redis for session storage
- In-memory caching for AI responses
- CDN for static assets

## Backup and Recovery

### 1. Configuration Backup
```bash
# Backup all configurations
kubectl get all -n aegis-orchestrator -o yaml > backup.yaml

# Backup secrets
kubectl get secret aegis-secrets -n aegis-orchestrator -o yaml > secrets-backup.yaml
```

### 2. Data Recovery
```bash
# Restore configuration
kubectl apply -f backup.yaml

# Restore secrets
kubectl apply -f secrets-backup.yaml
```

## Support

### Contact Information
- **Author:** Hasibur Rashid
- **Email:** atm.hasibur.rashid20367@gmail.com
- **Documentation:** See docs/ directory
- **Issues:** Create GitHub issue

### Resources
- **Architecture:** docs/architecture.md
- **Demo Scenarios:** docs/demo-scenarios.md
- **Security Review:** SECURITY_REVIEW.md
- **Cleanup Report:** CLEANUP_REPORT.md

---

*This deployment guide was created on 2024-09-18 by Hasibur Rashid.*
