# Aegis Orchestrator - An Intelligent Supply Chain & Customer Experience Agent

**Authors:** 
- Savnvancan (sanworktech@gmail.com)
- Hasibur Rashid (atm.hasibur.rashid20367@gmail.com)

## Overview

Aegis Orchestrator is an AI-powered external brain for the Online Boutique that autonomously optimizes the entire order lifecycle. It predicts demand, personalizes interactions, solves fulfillment problems in real-time, and proactively communicates with customers—transforming a static microservice application into a responsive, intelligent ecosystem.

## Key Features

- **Intelligent Personalization**: AI-powered product recommendations and dynamic pricing
- **Predictive Inventory Management**: Proactive stock monitoring and fulfillment optimization
- **Proactive Customer Communication**: Automated, contextual customer interactions
- **Anomaly Resolution**: Real-time problem detection and intelligent solutions
- **Zero Code Modification**: Operates entirely through existing APIs

## Architecture

The system consists of several containerized microservices deployed on GKE:

- **MCP Server**: Safe gateway between AI agents and Online Boutique APIs
- **Orchestrator Agent**: Central decision-maker using Google Gemini
- **Specialized Agent Pods**: Personalization, Inventory, Customer Comms, and Anomaly Resolver agents
- **Agent2Agent (A2A) Communication**: Inter-agent coordination protocol

## Technology Stack

- **GKE**: Container orchestration and scaling
- **Google Gemini**: AI reasoning and natural language processing
- **MCP (Model Context Protocol)**: Safe API integration
- **A2A (Agent2Agent)**: Inter-agent communication
- **Python**: Core implementation language
- **Kubernetes**: Container management

## Quick Start

1. **Prerequisites**:
   - Google Cloud Platform account
   - GKE cluster running
   - Online Boutique deployed

2. **Deploy the Orchestrator**:
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd aegis-orchestrator
   
   # Deploy to GKE
   kubectl apply -f k8s/
   ```

3. **Configure Environment**:
   ```bash
   # Set your Gemini API key
   export GEMINI_API_KEY="your-api-key"
   
   # Update configuration
   kubectl apply -f k8s/configmap.yaml
   ```

4. **Monitor the System**:
   ```bash
   # Check agent status
   kubectl get pods -l app=aegis-orchestrator
   
   # View logs
   kubectl logs -f deployment/orchestrator-agent
   ```

## Demo Scenarios

### Scenario 1: Intelligent Upsell & Personalized Checkout
- User adds "yellow sweater" to cart
- AI suggests matching "denim jeans" with 10% bundle discount
- Demonstrates increased AOV and improved UX

### Scenario 2: Predictive Inventory & Dynamic Rerouting
- AI predicts stock shortage in East Coast warehouse
- Automatically reroutes orders to West Coast warehouse
- Proactively notifies customers with compensation

### Scenario 3: Proactive Problem Solver
- Payment processing failure detected
- AI places orders in pending state
- Sends reassuring communication to customers

## Project Structure

```
aegis-orchestrator/
├── agents/                 # Specialized AI agents
│   ├── orchestrator/      # Central coordination agent
│   ├── personalization/   # Recommendation engine
│   ├── inventory/         # Stock management
│   ├── customer_comms/    # Communication agent
│   └── anomaly_resolver/  # Problem resolution
├── mcp_server/            # Model Context Protocol server
├── k8s/                   # Kubernetes manifests
├── config/                # Configuration files
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For questions or issues, please open an issue in the GitHub repository.
