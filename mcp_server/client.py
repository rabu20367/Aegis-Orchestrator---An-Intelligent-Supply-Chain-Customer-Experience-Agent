"""HTTP client for communicating with Online Boutique APIs."""

import asyncio
import time
from typing import Any, Dict, List, Optional
import httpx
from config.settings import settings
from mcp_server.models import MCPRequest, MCPResponse, MCPError


class BoutiqueAPIClient:
    """HTTP client for Online Boutique API interactions."""
    
    def __init__(self):
        self.base_url = settings.boutique_api_url
        self.timeout = httpx.Timeout(30.0)
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def _make_request(self, request: MCPRequest) -> MCPResponse:
        """Make an HTTP request to the Online Boutique API."""
        start_time = time.time()
        
        try:
            # Build URL
            url = f"{self.base_url}{request.endpoint}"
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Aegis-Orchestrator/1.0",
                **(request.headers or {})
            }
            
            # Make the request
            response = await self.client.request(
                method=request.method.value,
                url=url,
                params=request.params,
                headers=headers,
                json=request.body,
                timeout=request.timeout
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Parse response
            try:
                data = response.json() if response.content else None
            except Exception:
                data = {"raw_content": response.text}
            
            return MCPResponse(
                request_id=request.request_id,
                status_code=response.status_code,
                success=200 <= response.status_code < 300,
                data=data,
                headers=dict(response.headers),
                execution_time_ms=execution_time
            )
            
        except httpx.TimeoutException:
            execution_time = (time.time() - start_time) * 1000
            return MCPResponse(
                request_id=request.request_id,
                status_code=408,
                success=False,
                error="Request timeout",
                execution_time_ms=execution_time
            )
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return MCPResponse(
                request_id=request.request_id,
                status_code=500,
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    # Product-related methods
    async def get_products(self, request_id: str, agent_id: str, 
                          category: Optional[str] = None) -> MCPResponse:
        """Get all products or products by category."""
        endpoint = "/products"
        params = {"category": category} if category else None
        
        request = MCPRequest(
            request_id=request_id,
            agent_id=agent_id,
            method="GET",
            endpoint=endpoint,
            params=params
        )
        return await self._make_request(request)
    
    async def get_product(self, request_id: str, agent_id: str, 
                         product_id: str) -> MCPResponse:
        """Get a specific product by ID."""
        request = MCPRequest(
            request_id=request_id,
            agent_id=agent_id,
            method="GET",
            endpoint=f"/products/{product_id}"
        )
        return await self._make_request(request)
    
    # Cart-related methods
    async def get_cart(self, request_id: str, agent_id: str, 
                      user_id: str) -> MCPResponse:
        """Get user's cart."""
        request = MCPRequest(
            request_id=request_id,
            agent_id=agent_id,
            method="GET",
            endpoint=f"/cart/{user_id}"
        )
        return await self._make_request(request)
    
    async def add_to_cart(self, request_id: str, agent_id: str, 
                         user_id: str, product_id: str, quantity: int) -> MCPResponse:
        """Add item to cart."""
        request = MCPRequest(
            request_id=request_id,
            agent_id=agent_id,
            method="POST",
            endpoint=f"/cart/{user_id}/items",
            body={
                "product_id": product_id,
                "quantity": quantity
            }
        )
        return await self._make_request(request)
    
    async def update_cart_item(self, request_id: str, agent_id: str, 
                              user_id: str, product_id: str, quantity: int) -> MCPResponse:
        """Update cart item quantity."""
        request = MCPRequest(
            request_id=request_id,
            agent_id=agent_id,
            method="PUT",
            endpoint=f"/cart/{user_id}/items/{product_id}",
            body={"quantity": quantity}
        )
        return await self._make_request(request)
    
    async def remove_from_cart(self, request_id: str, agent_id: str, 
                              user_id: str, product_id: str) -> MCPResponse:
        """Remove item from cart."""
        request = MCPRequest(
            request_id=request_id,
            agent_id=agent_id,
            method="DELETE",
            endpoint=f"/cart/{user_id}/items/{product_id}"
        )
        return await self._make_request(request)
    
    # Order-related methods
    async def create_order(self, request_id: str, agent_id: str, 
                          user_id: str, order_data: Dict[str, Any]) -> MCPResponse:
        """Create a new order."""
        request = MCPRequest(
            request_id=request_id,
            agent_id=agent_id,
            method="POST",
            endpoint=f"/orders/{user_id}",
            body=order_data
        )
        return await self._make_request(request)
    
    async def get_order(self, request_id: str, agent_id: str, 
                       order_id: str) -> MCPResponse:
        """Get order details."""
        request = MCPRequest(
            request_id=request_id,
            agent_id=agent_id,
            method="GET",
            endpoint=f"/orders/{order_id}"
        )
        return await self._make_request(request)
    
    async def get_user_orders(self, request_id: str, agent_id: str, 
                             user_id: str) -> MCPResponse:
        """Get all orders for a user."""
        request = MCPRequest(
            request_id=request_id,
            agent_id=agent_id,
            method="GET",
            endpoint=f"/orders/user/{user_id}"
        )
        return await self._make_request(request)
    
    # User-related methods
    async def get_user(self, request_id: str, agent_id: str, 
                      user_id: str) -> MCPResponse:
        """Get user information."""
        request = MCPRequest(
            request_id=request_id,
            agent_id=agent_id,
            method="GET",
            endpoint=f"/users/{user_id}"
        )
        return await self._make_request(request)
    
    async def get_user_by_email(self, request_id: str, agent_id: str, 
                               email: str) -> MCPResponse:
        """Get user by email."""
        request = MCPRequest(
            request_id=request_id,
            agent_id=agent_id,
            method="GET",
            endpoint=f"/users/email/{email}"
        )
        return await self._make_request(request)
    
    # Generic method for custom endpoints
    async def make_request(self, request: MCPRequest) -> MCPResponse:
        """Make a generic request to the API."""
        return await self._make_request(request)
