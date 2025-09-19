"""Base agent class for Aegis Orchestrator agents."""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel

from config.settings import settings


class AgentMessage(BaseModel):
    """Message model for agent communication."""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: float
    correlation_id: Optional[str] = None


class AgentResponse(BaseModel):
    """Response model for agent operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float


class BaseAgent(ABC):
    """Base class for all Aegis Orchestrator agents."""
    
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name}")
        self.mcp_client = httpx.AsyncClient(
            base_url=f"http://mcp-server:{settings.mcp_server_port}",
            timeout=30.0
        )
        self.is_running = False
        self.message_queue = asyncio.Queue()
        
    async def start(self):
        """Start the agent."""
        self.is_running = True
        self.logger.info(f"Starting {self.agent_name} agent")
        
        # Start message processing loop
        asyncio.create_task(self._message_loop())
        
        # Start agent-specific initialization
        await self.initialize()
        
        self.logger.info(f"{self.agent_name} agent started successfully")
    
    async def stop(self):
        """Stop the agent."""
        self.is_running = False
        self.logger.info(f"Stopping {self.agent_name} agent")
        
        # Stop agent-specific cleanup
        await self.cleanup()
        
        # Close HTTP client
        await self.mcp_client.aclose()
        
        self.logger.info(f"{self.agent_name} agent stopped")
    
    async def _message_loop(self):
        """Main message processing loop."""
        while self.is_running:
            try:
                # Wait for messages with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                await self._process_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    async def _process_message(self, message: AgentMessage):
        """Process incoming message."""
        try:
            self.logger.debug(f"Processing message {message.message_id} from {message.sender_id}")
            
            # Route message to appropriate handler
            response = await self.handle_message(message)
            
            # Send response if needed
            if response and message.correlation_id:
                await self.send_message(
                    recipient_id=message.sender_id,
                    message_type="response",
                    content=response.dict(),
                    correlation_id=message.correlation_id
                )
                
        except Exception as e:
            self.logger.error(f"Error handling message {message.message_id}: {e}")
    
    async def send_message(self, recipient_id: str, message_type: str, 
                          content: Dict[str, Any], correlation_id: Optional[str] = None):
        """Send message to another agent."""
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            timestamp=asyncio.get_event_loop().time(),
            correlation_id=correlation_id
        )
        
        # In a real implementation, this would use A2A protocol
        # For now, we'll use a simple HTTP-based approach
        try:
            response = await self.mcp_client.post(
                f"/agents/{recipient_id}/message",
                json=message.dict()
            )
            response.raise_for_status()
        except Exception as e:
            self.logger.error(f"Failed to send message to {recipient_id}: {e}")
    
    async def make_mcp_request(self, method: str, endpoint: str, 
                              params: Optional[Dict] = None, 
                              body: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the MCP server."""
        request_data = {
            "request_id": str(uuid.uuid4()),
            "agent_id": self.agent_id,
            "method": method,
            "endpoint": endpoint,
            "params": params,
            "body": body
        }
        
        try:
            response = await self.mcp_client.post("/mcp/request", json=request_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"MCP request failed: {e}")
            raise
    
    @abstractmethod
    async def initialize(self):
        """Initialize agent-specific resources."""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup agent-specific resources."""
        pass
    
    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> Optional[AgentResponse]:
        """Handle incoming message."""
        pass
    
    async def get_products(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get products from the boutique."""
        response = await self.make_mcp_request("GET", "/products", params={"category": category})
        return response.get("data", {}).get("products", [])
    
    async def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get a specific product."""
        response = await self.make_mcp_request("GET", f"/products/{product_id}")
        return response.get("data", {})
    
    async def get_user_cart(self, user_id: str) -> Dict[str, Any]:
        """Get user's cart."""
        response = await self.make_mcp_request("GET", f"/cart/{user_id}")
        return response.get("data", {})
    
    async def add_to_cart(self, user_id: str, product_id: str, quantity: int) -> Dict[str, Any]:
        """Add item to user's cart."""
        response = await self.make_mcp_request(
            "POST", 
            f"/cart/{user_id}/items",
            body={"product_id": product_id, "quantity": quantity}
        )
        return response.get("data", {})
    
    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get order details."""
        response = await self.make_mcp_request("GET", f"/orders/{order_id}")
        return response.get("data", {})
    
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user information."""
        response = await self.make_mcp_request("GET", f"/users/{user_id}")
        return response.get("data", {})
