"""Tests for MCP Server."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from mcp_server.client import BoutiqueAPIClient
from mcp_server.models import MCPRequest, MCPRequestType


class TestBoutiqueAPIClient:
    """Test cases for BoutiqueAPIClient."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return BoutiqueAPIClient()
    
    @pytest.mark.asyncio
    async def test_get_products(self, client):
        """Test getting products."""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "data": {"products": [{"id": "1", "name": "Test Product"}]}
            }
            
            response = await client.get_products("test-agent", "test-request")
            
            assert response["success"] is True
            assert "products" in response["data"]
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_product(self, client):
        """Test getting a specific product."""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "data": {"id": "1", "name": "Test Product"}
            }
            
            response = await client.get_product("test-agent", "test-request", "1")
            
            assert response["success"] is True
            assert response["data"]["id"] == "1"
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_to_cart(self, client):
        """Test adding item to cart."""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "data": {"message": "Item added to cart"}
            }
            
            response = await client.add_to_cart("test-agent", "test-request", "user1", "product1", 2)
            
            assert response["success"] is True
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_error_handling(self, client):
        """Test error handling in make_request."""
        with patch.object(client.client, 'request') as mock_request:
            mock_request.side_effect = Exception("Network error")
            
            request = MCPRequest(
                request_id="test-request",
                agent_id="test-agent",
                method=MCPRequestType.GET,
                endpoint="/test"
            )
            
            response = await client._make_request(request)
            
            assert response.success is False
            assert response.status_code == 500
            assert "Network error" in response.error


class TestMCPModels:
    """Test cases for MCP models."""
    
    def test_mcp_request_creation(self):
        """Test MCP request model creation."""
        request = MCPRequest(
            request_id="test-request",
            agent_id="test-agent",
            method=MCPRequestType.GET,
            endpoint="/test"
        )
        
        assert request.request_id == "test-request"
        assert request.agent_id == "test-agent"
        assert request.method == MCPRequestType.GET
        assert request.endpoint == "/test"
    
    def test_mcp_response_creation(self):
        """Test MCP response model creation."""
        response = MCPResponse(
            request_id="test-request",
            status_code=200,
            success=True,
            data={"test": "data"},
            execution_time_ms=100.0
        )
        
        assert response.request_id == "test-request"
        assert response.status_code == 200
        assert response.success is True
        assert response.data == {"test": "data"}
        assert response.execution_time_ms == 100.0


if __name__ == "__main__":
    pytest.main([__file__])
