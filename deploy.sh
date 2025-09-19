#!/bin/bash

# Aegis Orchestrator Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="aegis-orchestrator"
REGISTRY="your-registry.com"  # Replace with your container registry
TAG="latest"

echo -e "${GREEN}🚀 Starting Aegis Orchestrator Deployment${NC}"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl is not installed or not in PATH${NC}"
    exit 1
fi

# Check if we're connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ Not connected to a Kubernetes cluster${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check if Online Boutique is deployed
if ! kubectl get namespace microservices-demo &> /dev/null; then
    echo -e "${YELLOW}⚠️  Online Boutique not found. Please deploy it first.${NC}"
    echo -e "${YELLOW}   You can deploy it using:${NC}"
    echo -e "${YELLOW}   kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/release/kubernetes-manifests.yaml${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create namespace
echo -e "${YELLOW}📦 Creating namespace...${NC}"
kubectl apply -f k8s/namespace.yaml

# Create secrets
echo -e "${YELLOW}🔐 Creating secrets...${NC}"
kubectl apply -f k8s/secret.yaml

# Create configmap
echo -e "${YELLOW}⚙️  Creating configmap...${NC}"
kubectl apply -f k8s/configmap.yaml

# Deploy Redis
echo -e "${YELLOW}🗄️  Deploying Redis...${NC}"
kubectl apply -f k8s/redis.yaml

# Wait for Redis to be ready
echo -e "${YELLOW}⏳ Waiting for Redis to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s

# Deploy MCP Server
echo -e "${YELLOW}🌐 Deploying MCP Server...${NC}"
kubectl apply -f k8s/mcp-server.yaml

# Wait for MCP Server to be ready
echo -e "${YELLOW}⏳ Waiting for MCP Server to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=mcp-server -n $NAMESPACE --timeout=300s

# Deploy agents
echo -e "${YELLOW}🤖 Deploying AI Agents...${NC}"

# Orchestrator Agent
echo -e "${YELLOW}  - Deploying Orchestrator Agent...${NC}"
kubectl apply -f k8s/orchestrator-agent.yaml

# Personalization Agent
echo -e "${YELLOW}  - Deploying Personalization Agent...${NC}"
kubectl apply -f k8s/personalization-agent.yaml

# Inventory Agent
echo -e "${YELLOW}  - Deploying Inventory Agent...${NC}"
kubectl apply -f k8s/inventory-agent.yaml

# Customer Communications Agent
echo -e "${YELLOW}  - Deploying Customer Communications Agent...${NC}"
kubectl apply -f k8s/customer-comms-agent.yaml

# Anomaly Resolver Agent
echo -e "${YELLOW}  - Deploying Anomaly Resolver Agent...${NC}"
kubectl apply -f k8s/anomaly-resolver-agent.yaml

# Wait for all agents to be ready
echo -e "${YELLOW}⏳ Waiting for all agents to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=aegis-orchestrator -n $NAMESPACE --timeout=600s

# Check deployment status
echo -e "${YELLOW}📊 Checking deployment status...${NC}"
kubectl get pods -n $NAMESPACE

# Get service URLs
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🎉 Aegis Orchestrator is now running!${NC}"
echo
echo -e "${YELLOW}📋 Service URLs:${NC}"
echo -e "  MCP Server: http://$(kubectl get service mcp-server -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo 'localhost'):8001"
echo -e "  Orchestrator: http://$(kubectl get service orchestrator-agent -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo 'localhost'):8000"
echo
echo -e "${YELLOW}🔍 To view logs:${NC}"
echo -e "  kubectl logs -f deployment/orchestrator-agent -n $NAMESPACE"
echo -e "  kubectl logs -f deployment/mcp-server -n $NAMESPACE"
echo
echo -e "${YELLOW}🛠️  To scale agents:${NC}"
echo -e "  kubectl scale deployment personalization-agent --replicas=3 -n $NAMESPACE"
echo
echo -e "${GREEN}🚀 Aegis Orchestrator is ready to optimize your Online Boutique!${NC}"
