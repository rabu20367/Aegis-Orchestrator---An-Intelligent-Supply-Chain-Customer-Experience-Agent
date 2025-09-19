"""MCP Server implementation for Aegis Orchestrator."""

import asyncio
import logging
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config.settings import settings
from mcp_server.client import BoutiqueAPIClient
from mcp_server.models import MCPRequest, MCPResponse, MCPError

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Aegis Orchestrator MCP Server",
    description="Model Context Protocol server for AI agent communication with Online Boutique",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global API client
api_client: BoutiqueAPIClient = None


@app.on_event("startup")
async def startup_event():
    """Initialize the MCP server."""
    global api_client
    api_client = BoutiqueAPIClient()
    logger.info("MCP Server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown."""
    global api_client
    if api_client:
        await api_client.close()
    logger.info("MCP Server shutdown complete")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp-server"}


@app.post("/mcp/request", response_model=MCPResponse)
async def handle_mcp_request(request: MCPRequest):
    """Handle MCP requests from AI agents."""
    try:
        logger.info(f"Processing MCP request {request.request_id} from agent {request.agent_id}")
        
        # Validate request
        if not request.request_id:
            request.request_id = str(uuid.uuid4())
        
        # Make the API call
        response = await api_client.make_request(request)
        
        logger.info(f"Request {request.request_id} completed with status {response.status_code}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing request {request.request_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Convenience endpoints for common operations
@app.get("/products")
async def get_products(category: str = None, agent_id: str = "system"):
    """Get products with optional category filter."""
    request_id = str(uuid.uuid4())
    response = await api_client.get_products(request_id, agent_id, category)
    
    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.error)
    
    return response.data


@app.get("/products/{product_id}")
async def get_product(product_id: str, agent_id: str = "system"):
    """Get a specific product."""
    request_id = str(uuid.uuid4())
    response = await api_client.get_product(request_id, agent_id, product_id)
    
    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.error)
    
    return response.data


@app.get("/cart/{user_id}")
async def get_cart(user_id: str, agent_id: str = "system"):
    """Get user's cart."""
    request_id = str(uuid.uuid4())
    response = await api_client.get_cart(request_id, agent_id, user_id)
    
    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.error)
    
    return response.data


@app.post("/cart/{user_id}/items")
async def add_to_cart(
    user_id: str, 
    product_id: str, 
    quantity: int, 
    agent_id: str = "system"
):
    """Add item to cart."""
    request_id = str(uuid.uuid4())
    response = await api_client.add_to_cart(request_id, agent_id, user_id, product_id, quantity)
    
    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.error)
    
    return response.data


@app.get("/orders/{order_id}")
async def get_order(order_id: str, agent_id: str = "system"):
    """Get order details."""
    request_id = str(uuid.uuid4())
    response = await api_client.get_order(request_id, agent_id, order_id)
    
    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.error)
    
    return response.data


@app.get("/users/{user_id}")
async def get_user(user_id: str, agent_id: str = "system"):
    """Get user information."""
    request_id = str(uuid.uuid4())
    response = await api_client.get_user(request_id, agent_id, user_id)
    
    if not response.success:
        raise HTTPException(status_code=response.status_code, detail=response.error)
    
    return response.data


if __name__ == "__main__":
    uvicorn.run(
        "mcp_server.server:app",
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
