# Aegis Orchestrator Deployment Guide

## Prerequisites

### 1. Google Cloud Platform Setup
- **GCP Account**: Active Google Cloud Platform account
- **Billing**: Enabled billing for the project
- **APIs**: Enable required APIs (GKE, AI Platform, etc.)
- **IAM**: Appropriate permissions for deployment

### 2. Required Tools
- **kubectl**: Kubernetes command-line tool
- **gcloud**: Google Cloud CLI
- **Docker**: Container runtime (for local development)
- **Git**: Version control system

### 3. Online Boutique
- **Deployed**: Online Boutique must be running on GKE
- **Accessible**: APIs must be accessible from Aegis Orchestrator
- **Healthy**: All services should be running normally

## Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd aegis-orchestrator
```

### 2. Configure Environment
```bash
# Copy environment template
cp config/env.example .env

# Edit configuration
nano .env
```

### 3. Set Gemini API Key
```bash
# Get your API key from Google AI Studio
export GEMINI_API_KEY="your_api_key_here"

# Or update the secret in Kubernetes
kubectl create secret generic aegis-secrets \
  --from-literal=GEMINI_API_KEY="your_api_key_here" \
  -n aegis-orchestrator
```

### 4. Deploy to GKE
```bash
# For Linux/Mac
./deploy.sh

# For Windows
.\deploy.ps1
```

## Detailed Deployment

### 1. GKE Cluster Setup

#### Create Cluster
```bash
# Create GKE cluster
gcloud container clusters create aegis-cluster \
  --zone=us-central1-a \
  --num-nodes=3 \
  --machine-type=e2-standard-4 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10 \
  --enable-autorepair \
  --enable-autoupgrade
```

#### Configure kubectl
```bash
# Get cluster credentials
gcloud container clusters get-credentials aegis-cluster --zone=us-central1-a

# Verify connection
kubectl get nodes
```

### 2. Deploy Online Boutique

#### Deploy Microservices Demo
```bash
# Deploy Online Boutique
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/release/kubernetes-manifests.yaml

# Wait for deployment
kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s
```

#### Verify Deployment
```bash
# Check all pods
kubectl get pods

# Get external IP
kubectl get service frontend-external
```

### 3. Deploy Aegis Orchestrator

#### Create Namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

#### Create Secrets
```bash
# Create secret with Gemini API key
kubectl create secret generic aegis-secrets \
  --from-literal=GEMINI_API_KEY="your_api_key_here" \
  --from-literal=GEMINI_MODEL="gemini-1.5-pro" \
  -n aegis-orchestrator
```

#### Create ConfigMap
```bash
kubectl apply -f k8s/configmap.yaml
```

#### Deploy Services
```bash
# Deploy Redis
kubectl apply -f k8s/redis.yaml

# Deploy MCP Server
kubectl apply -f k8s/mcp-server.yaml

# Deploy Agents
kubectl apply -f k8s/orchestrator-agent.yaml
kubectl apply -f k8s/personalization-agent.yaml
kubectl apply -f k8s/inventory-agent.yaml
kubectl apply -f k8s/customer-comms-agent.yaml
kubectl apply -f k8s/anomaly-resolver-agent.yaml
```

### 4. Verify Deployment

#### Check Pod Status
```bash
kubectl get pods -n aegis-orchestrator
```

#### Check Services
```bash
kubectl get services -n aegis-orchestrator
```

#### View Logs
```bash
# MCP Server logs
kubectl logs -f deployment/mcp-server -n aegis-orchestrator

# Orchestrator Agent logs
kubectl logs -f deployment/orchestrator-agent -n aegis-orchestrator
```

## Configuration

### 1. Environment Variables

#### Required Variables
- `GEMINI_API_KEY`: Your Google Gemini API key
- `GEMINI_MODEL`: Gemini model to use (default: gemini-1.5-pro)

#### Optional Variables
- `BOUTIQUE_API_URL`: Online Boutique API URL
- `LOG_LEVEL`: Logging level (default: INFO)
- `REDIS_URL`: Redis connection URL
- `A2A_BROKER_URL`: Agent-to-agent broker URL

### 2. Resource Limits

#### CPU and Memory
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

#### Scaling
```bash
# Scale personalization agent
kubectl scale deployment personalization-agent --replicas=3 -n aegis-orchestrator

# Scale customer comms agent
kubectl scale deployment customer-comms-agent --replicas=2 -n aegis-orchestrator
```

### 3. Monitoring Setup

#### Prometheus (Optional)
```bash
# Install Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

#### Grafana (Optional)
```bash
# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
```

## Troubleshooting

### 1. Common Issues

#### Pods Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n aegis-orchestrator

# Check logs
kubectl logs <pod-name> -n aegis-orchestrator
```

#### API Connection Issues
```bash
# Test MCP server
kubectl port-forward svc/mcp-server 8001:8001 -n aegis-orchestrator
curl http://localhost:8001/health

# Test Online Boutique
kubectl port-forward svc/frontend 80:80
curl http://localhost/api/products
```

#### AI Agent Issues
```bash
# Check Gemini API key
kubectl get secret aegis-secrets -n aegis-orchestrator -o yaml

# Test API connectivity
kubectl exec -it <orchestrator-pod> -n aegis-orchestrator -- python -c "import google.generativeai as genai; print('API key valid')"
```

### 2. Debug Commands

#### Check Resource Usage
```bash
kubectl top pods -n aegis-orchestrator
kubectl top nodes
```

#### Check Events
```bash
kubectl get events -n aegis-orchestrator --sort-by='.lastTimestamp'
```

#### Check Network
```bash
kubectl get networkpolicies -n aegis-orchestrator
kubectl get ingress -n aegis-orchestrator
```

### 3. Log Analysis

#### Centralized Logging
```bash
# View all logs
kubectl logs -f -l app=aegis-orchestrator -n aegis-orchestrator

# Filter by component
kubectl logs -f deployment/orchestrator-agent -n aegis-orchestrator | grep "ERROR"
```

#### Log Aggregation
```bash
# Install Fluentd (optional)
kubectl apply -f https://raw.githubusercontent.com/fluent/fluentd-kubernetes-daemonset/master/fluentd-daemonset.yaml
```

## Security

### 1. Network Security

#### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: aegis-network-policy
  namespace: aegis-orchestrator
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: microservices-demo
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: microservices-demo
```

#### Service Mesh (Optional)
```bash
# Install Istio
curl -L https://istio.io/downloadIstio | sh -
istioctl install --set values.defaultRevision=default
```

### 2. Secret Management

#### External Secret Management
```bash
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace
```

#### Secret Rotation
```bash
# Update secret
kubectl create secret generic aegis-secrets \
  --from-literal=GEMINI_API_KEY="new_api_key" \
  -n aegis-orchestrator --dry-run=client -o yaml | kubectl apply -f -

# Restart deployments
kubectl rollout restart deployment -n aegis-orchestrator
```

## Maintenance

### 1. Updates

#### Rolling Updates
```bash
# Update image
kubectl set image deployment/orchestrator-agent orchestrator-agent=aegis-orchestrator/orchestrator-agent:v2.0.0 -n aegis-orchestrator

# Check rollout status
kubectl rollout status deployment/orchestrator-agent -n aegis-orchestrator
```

#### Rollback
```bash
# Rollback to previous version
kubectl rollout undo deployment/orchestrator-agent -n aegis-orchestrator
```

### 2. Backup

#### Configuration Backup
```bash
# Backup all resources
kubectl get all -n aegis-orchestrator -o yaml > aegis-backup.yaml

# Backup secrets
kubectl get secrets -n aegis-orchestrator -o yaml > aegis-secrets-backup.yaml
```

#### Data Backup
```bash
# Backup Redis data
kubectl exec -it deployment/redis -n aegis-orchestrator -- redis-cli BGSAVE
```

### 3. Monitoring

#### Health Checks
```bash
# Check all deployments
kubectl get deployments -n aegis-orchestrator

# Check pod health
kubectl get pods -n aegis-orchestrator -o wide
```

#### Performance Monitoring
```bash
# Check resource usage
kubectl top pods -n aegis-orchestrator

# Check events
kubectl get events -n aegis-orchestrator --sort-by='.lastTimestamp'
```

## Scaling

### 1. Horizontal Scaling

#### Auto Scaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: personalization-agent-hpa
  namespace: aegis-orchestrator
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: personalization-agent
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

#### Manual Scaling
```bash
# Scale specific deployment
kubectl scale deployment personalization-agent --replicas=5 -n aegis-orchestrator
```

### 2. Vertical Scaling

#### Resource Requests
```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "1000m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

#### VPA (Vertical Pod Autoscaler)
```bash
# Install VPA
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-0.13.0/vpa-release.yaml
```

## Cleanup

### 1. Remove Aegis Orchestrator
```bash
# Delete all resources
kubectl delete namespace aegis-orchestrator

# Or delete individual components
kubectl delete -f k8s/
```

### 2. Remove Online Boutique
```bash
# Delete microservices demo
kubectl delete -f https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/release/kubernetes-manifests.yaml
```

### 3. Remove GKE Cluster
```bash
# Delete cluster
gcloud container clusters delete aegis-cluster --zone=us-central1-a
```

## Support

### 1. Documentation
- **Architecture**: See `docs/architecture.md`
- **Demo Scenarios**: See `docs/demo-scenarios.md`
- **API Reference**: See `docs/api-reference.md`

### 2. Community
- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and share ideas
- **Contributing**: Submit pull requests

### 3. Professional Support
- **Google Cloud Support**: For GKE and AI Platform issues
- **Consulting**: For custom implementations
- **Training**: For team education and onboarding
