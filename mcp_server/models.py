"""Pydantic models for MCP Server."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class MCPRequestType(str, Enum):
    """MCP request types."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class MCPRequest(BaseModel):
    """MCP request model."""
    request_id: str = Field(..., description="Unique request identifier")
    agent_id: str = Field(..., description="ID of the requesting agent")
    method: MCPRequestType = Field(..., description="HTTP method")
    endpoint: str = Field(..., description="API endpoint path")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Request headers")
    body: Optional[Dict[str, Any]] = Field(default=None, description="Request body")
    timeout: Optional[int] = Field(default=30, description="Request timeout in seconds")


class MCPResponse(BaseModel):
    """MCP response model."""
    request_id: str = Field(..., description="Original request identifier")
    status_code: int = Field(..., description="HTTP status code")
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if any")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Response headers")
    execution_time_ms: float = Field(..., description="Request execution time in milliseconds")


class MCPError(BaseModel):
    """MCP error model."""
    request_id: str = Field(..., description="Original request identifier")
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class Product(BaseModel):
    """Product model from Online Boutique."""
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    picture: str = Field(..., description="Product image URL")
    price_usd: Dict[str, str] = Field(..., description="Product price")
    categories: List[str] = Field(default=[], description="Product categories")


class CartItem(BaseModel):
    """Cart item model."""
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(..., description="Quantity")
    price: float = Field(..., description="Item price")


class Order(BaseModel):
    """Order model from Online Boutique."""
    order_id: str = Field(..., description="Order ID")
    shipping_tracking_id: str = Field(..., description="Shipping tracking ID")
    shipping_cost: Dict[str, str] = Field(..., description="Shipping cost")
    total_amount: Dict[str, str] = Field(..., description="Total order amount")
    items: List[CartItem] = Field(..., description="Order items")
    shipping_address: Dict[str, str] = Field(..., description="Shipping address")
    email: str = Field(..., description="Customer email")


class User(BaseModel):
    """User model from Online Boutique."""
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    created_at: str = Field(..., description="Account creation timestamp")


class InventoryItem(BaseModel):
    """Inventory item model."""
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(..., description="Available quantity")
    warehouse: str = Field(..., description="Warehouse location")
    last_updated: str = Field(..., description="Last inventory update timestamp")
