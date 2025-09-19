# Aegis Orchestrator Deployment Script for Windows PowerShell

param(
    [string]$Namespace = "aegis-orchestrator",
    [string]$Registry = "your-registry.com",  # Replace with your container registry
    [string]$Tag = "latest"
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"

Write-Host "🚀 Starting Aegis Orchestrator Deployment" -ForegroundColor $Green

# Check if kubectl is available
try {
    kubectl version --client | Out-Null
} catch {
    Write-Host "❌ kubectl is not installed or not in PATH" -ForegroundColor $Red
    exit 1
}

# Check if we're connected to a cluster
try {
    kubectl cluster-info | Out-Null
} catch {
    Write-Host "❌ Not connected to a Kubernetes cluster" -ForegroundColor $Red
    exit 1
}

Write-Host "📋 Checking prerequisites..." -ForegroundColor $Yellow

# Check if Online Boutique is deployed
try {
    kubectl get namespace microservices-demo | Out-Null
} catch {
    Write-Host "⚠️  Online Boutique not found. Please deploy it first." -ForegroundColor $Yellow
    Write-Host "   You can deploy it using:" -ForegroundColor $Yellow
    Write-Host "   kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/release/kubernetes-manifests.yaml" -ForegroundColor $Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

# Create namespace
Write-Host "📦 Creating namespace..." -ForegroundColor $Yellow
kubectl apply -f k8s/namespace.yaml

# Create secrets
Write-Host "🔐 Creating secrets..." -ForegroundColor $Yellow
kubectl apply -f k8s/secret.yaml

# Create configmap
Write-Host "⚙️  Creating configmap..." -ForegroundColor $Yellow
kubectl apply -f k8s/configmap.yaml

# Deploy Redis
Write-Host "🗄️  Deploying Redis..." -ForegroundColor $Yellow
kubectl apply -f k8s/redis.yaml

# Wait for Redis to be ready
Write-Host "⏳ Waiting for Redis to be ready..." -ForegroundColor $Yellow
kubectl wait --for=condition=ready pod -l app=redis -n $Namespace --timeout=300s

# Deploy MCP Server
Write-Host "🌐 Deploying MCP Server..." -ForegroundColor $Yellow
kubectl apply -f k8s/mcp-server.yaml

# Wait for MCP Server to be ready
Write-Host "⏳ Waiting for MCP Server to be ready..." -ForegroundColor $Yellow
kubectl wait --for=condition=ready pod -l app=mcp-server -n $Namespace --timeout=300s

# Deploy agents
Write-Host "🤖 Deploying AI Agents..." -ForegroundColor $Yellow

# Orchestrator Agent
Write-Host "  - Deploying Orchestrator Agent..." -ForegroundColor $Yellow
kubectl apply -f k8s/orchestrator-agent.yaml

# Personalization Agent
Write-Host "  - Deploying Personalization Agent..." -ForegroundColor $Yellow
kubectl apply -f k8s/personalization-agent.yaml

# Inventory Agent
Write-Host "  - Deploying Inventory Agent..." -ForegroundColor $Yellow
kubectl apply -f k8s/inventory-agent.yaml

# Customer Communications Agent
Write-Host "  - Deploying Customer Communications Agent..." -ForegroundColor $Yellow
kubectl apply -f k8s/customer-comms-agent.yaml

# Anomaly Resolver Agent
Write-Host "  - Deploying Anomaly Resolver Agent..." -ForegroundColor $Yellow
kubectl apply -f k8s/anomaly-resolver-agent.yaml

# Wait for all agents to be ready
Write-Host "⏳ Waiting for all agents to be ready..." -ForegroundColor $Yellow
kubectl wait --for=condition=ready pod -l app=aegis-orchestrator -n $Namespace --timeout=600s

# Check deployment status
Write-Host "📊 Checking deployment status..." -ForegroundColor $Yellow
kubectl get pods -n $Namespace

# Get service URLs
Write-Host "✅ Deployment completed successfully!" -ForegroundColor $Green
Write-Host "🎉 Aegis Orchestrator is now running!" -ForegroundColor $Green
Write-Host ""
Write-Host "📋 Service URLs:" -ForegroundColor $Yellow
Write-Host "  MCP Server: http://localhost:8001" -ForegroundColor $Yellow
Write-Host "  Orchestrator: http://localhost:8000" -ForegroundColor $Yellow
Write-Host ""
Write-Host "🔍 To view logs:" -ForegroundColor $Yellow
Write-Host "  kubectl logs -f deployment/orchestrator-agent -n $Namespace" -ForegroundColor $Yellow
Write-Host "  kubectl logs -f deployment/mcp-server -n $Namespace" -ForegroundColor $Yellow
Write-Host ""
Write-Host "🛠️  To scale agents:" -ForegroundColor $Yellow
Write-Host "  kubectl scale deployment personalization-agent --replicas=3 -n $Namespace" -ForegroundColor $Yellow
Write-Host ""
Write-Host "🚀 Aegis Orchestrator is ready to optimize your Online Boutique!" -ForegroundColor $Green
