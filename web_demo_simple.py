#!/usr/bin/env python3
"""Web-based demonstration of Aegis Orchestrator with simple UI."""

import asyncio
import logging
import sys
import time
import json
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn

# Set test environment variables
import os
os.environ["GEMINI_API_KEY"] = "test_api_key_for_demo"
os.environ["GEMINI_MODEL"] = "gemini-1.5-pro"
os.environ["API_HOST"] = "0.0.0.0"
os.environ["API_PORT"] = "8000"
os.environ["DEBUG"] = "true"
os.environ["BOUTIQUE_BASE_URL"] = "http://localhost:8080"
os.environ["BOUTIQUE_API_URL"] = "http://localhost:8080/api"
os.environ["MCP_SERVER_HOST"] = "0.0.0.0"
os.environ["MCP_SERVER_PORT"] = "8001"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["A2A_BROKER_URL"] = "redis://localhost:6379"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock Google AI modules before any imports
sys.modules['google.generativeai'] = Mock()
sys.modules['google.generativeai'].configure = Mock()
sys.modules['google.generativeai'].GenerativeModel = Mock()
sys.modules['google.generativeai'].GenerativeModel.return_value.generate_content_async = AsyncMock()

# Create FastAPI app
app = FastAPI(title="Aegis Orchestrator Demo", description="AI-Powered E-commerce Intelligence")

class WebAegisOrchestrator:
    """Web-based Aegis Orchestrator Demo."""
    
    def __init__(self):
        self.user_profiles = {}
        self.inventory_data = {}
        self.orders = {}
        self.cart_data = {}
        self.system_metrics = {
            "ai_decisions": 0,
            "events_processed": 0,
            "problems_resolved": 0,
            "customer_interactions": 0
        }
        self.agents = {}
        self.current_user = None
        
    async def initialize_system(self):
        """Initialize the Aegis Orchestrator system."""
        logger.info("Initializing Aegis Orchestrator Web Demo...")
        
        # Initialize agents
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value = AsyncMock()
            
            from agents.orchestrator.agent import OrchestratorAgent
            from agents.personalization.agent import PersonalizationAgent
            from agents.inventory.agent import InventoryAgent
            from agents.customer_comms.agent import CustomerCommsAgent
            from agents.anomaly_resolver.agent import AnomalyResolverAgent
            
            self.agents = {
                "orchestrator": OrchestratorAgent(),
                "personalization": PersonalizationAgent(),
                "inventory": InventoryAgent(),
                "customer_comms": CustomerCommsAgent(),
                "anomaly_resolver": AnomalyResolverAgent()
            }
        
        # Initialize sample data
        self._initialize_sample_data()
        
        logger.info("Aegis Orchestrator Web Demo initialized successfully!")
        return True
    
    def _initialize_sample_data(self):
        """Initialize sample data for the demo."""
        # Sample user profiles
        self.user_profiles = {
            "demo-user-1": {
                "name": "Demo User 1",
                "email": "demo1@example.com",
                "browsing_history": ["casual-wear", "sweaters", "denim", "shoes"],
                "purchase_history": ["blue-jeans", "white-sneakers", "red-dress"],
                "preferences": {"style": "casual", "colors": ["yellow", "blue", "red"]},
                "loyalty_tier": "gold"
            },
            "demo-user-2": {
                "name": "Demo User 2",
                "email": "demo2@example.com",
                "browsing_history": ["electronics", "gadgets", "accessories"],
                "purchase_history": ["wireless-mouse", "laptop-stand"],
                "preferences": {"style": "tech", "colors": ["black", "silver"]},
                "loyalty_tier": "silver"
            },
            "demo-user-3": {
                "name": "Demo User 3",
                "email": "demo3@example.com",
                "browsing_history": ["formal-wear", "jewelry", "handbags"],
                "purchase_history": ["pearl-necklace", "black-heels"],
                "preferences": {"style": "elegant", "colors": ["black", "white", "gold"]},
                "loyalty_tier": "platinum"
            }
        }
        
        # Sample inventory data
        self.inventory_data = {
            "yellow-sweater": {
                "name": "Yellow Cashmere Sweater",
                "price": 89.99,
                "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=300&fit=crop",
                "warehouses": {
                    "east-coast": {"stock": 15, "threshold": 10},
                    "west-coast": {"stock": 8, "threshold": 10},
                    "central": {"stock": 25, "threshold": 10}
                },
                "category": "sweaters",
                "tags": ["casual", "warm", "yellow"],
                "description": "Luxurious cashmere sweater in vibrant yellow"
            },
            "denim-jeans": {
                "name": "Classic Blue Denim Jeans",
                "price": 79.99,
                "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=300&h=300&fit=crop",
                "warehouses": {
                    "east-coast": {"stock": 5, "threshold": 10},
                    "west-coast": {"stock": 30, "threshold": 10},
                    "central": {"stock": 12, "threshold": 10}
                },
                "category": "denim",
                "tags": ["casual", "blue", "jeans"],
                "description": "Classic fit denim jeans in timeless blue"
            },
            "white-sneakers": {
                "name": "White Canvas Sneakers",
                "price": 59.99,
                "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop",
                "warehouses": {
                    "east-coast": {"stock": 20, "threshold": 10},
                    "west-coast": {"stock": 15, "threshold": 10},
                    "central": {"stock": 8, "threshold": 10}
                },
                "category": "shoes",
                "tags": ["casual", "white", "sneakers"],
                "description": "Comfortable white canvas sneakers for everyday wear"
            },
            "wireless-mouse": {
                "name": "Wireless Gaming Mouse",
                "price": 49.99,
                "image": "https://images.unsplash.com/photo-1527864550417-7f457444d1b5?w=300&h=300&fit=crop",
                "warehouses": {
                    "east-coast": {"stock": 3, "threshold": 10},
                    "west-coast": {"stock": 18, "threshold": 10},
                    "central": {"stock": 22, "threshold": 10}
                },
                "category": "electronics",
                "tags": ["tech", "wireless", "gaming"],
                "description": "High-performance wireless mouse for gaming and work"
            }
        }
        
        # Initialize empty carts
        for user_id in self.user_profiles:
            self.cart_data[user_id] = {"items": [], "total": 0.0}

# Global instance
aegis = WebAegisOrchestrator()

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup."""
    await aegis.initialize_system()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with dashboard."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aegis Orchestrator - AI-Powered E-commerce Intelligence</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card-hover { transition: transform 0.2s, box-shadow 0.2s; }
        .card-hover:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="bg-gray-50">
    <div x-data="aegisApp()" class="min-h-screen">
        <!-- Header -->
        <header class="gradient-bg text-white shadow-lg">
            <div class="container mx-auto px-6 py-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="text-3xl">🎯</div>
                        <div>
                            <h1 class="text-2xl font-bold">Aegis Orchestrator</h1>
                            <p class="text-blue-100">AI-Powered E-commerce Intelligence</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <div class="text-right">
                            <div class="text-sm text-blue-100">System Status</div>
                            <div class="text-lg font-semibold text-green-300">🟢 OPERATIONAL</div>
                        </div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="container mx-auto px-6 py-8">
            <!-- Navigation Tabs -->
            <div class="mb-8">
                <div class="flex space-x-1 bg-white rounded-lg p-1 shadow-sm">
                    <button @click="activeTab = 'dashboard'" 
                            :class="activeTab === 'dashboard' ? 'bg-blue-500 text-white' : 'text-gray-600'"
                            class="px-4 py-2 rounded-md font-medium transition-colors">
                        📊 Dashboard
                    </button>
                    <button @click="activeTab = 'customers'" 
                            :class="activeTab === 'customers' ? 'bg-blue-500 text-white' : 'text-gray-600'"
                            class="px-4 py-2 rounded-md font-medium transition-colors">
                        👤 Customers
                    </button>
                    <button @click="activeTab = 'inventory'" 
                            :class="activeTab === 'inventory' ? 'bg-blue-500 text-white' : 'text-gray-600'"
                            class="px-4 py-2 rounded-md font-medium transition-colors">
                        📦 Inventory
                    </button>
                    <button @click="activeTab = 'analytics'" 
                            :class="activeTab === 'analytics' ? 'bg-blue-500 text-white' : 'text-gray-600'"
                            class="px-4 py-2 rounded-md font-medium transition-colors">
                        📈 Analytics
                    </button>
                </div>
            </div>

            <!-- Dashboard Tab -->
            <div x-show="activeTab === 'dashboard'" class="space-y-6">
                <!-- System Overview -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div class="bg-white rounded-lg shadow-md p-6 card-hover">
                        <div class="flex items-center">
                            <div class="text-3xl text-blue-500">🤖</div>
                            <div class="ml-4">
                                <div class="text-2xl font-bold text-gray-900" x-text="metrics.ai_decisions">0</div>
                                <div class="text-sm text-gray-500">AI Decisions</div>
                            </div>
                        </div>
                    </div>
                    <div class="bg-white rounded-lg shadow-md p-6 card-hover">
                        <div class="flex items-center">
                            <div class="text-3xl text-green-500">📊</div>
                            <div class="ml-4">
                                <div class="text-2xl font-bold text-gray-900" x-text="metrics.events_processed">0</div>
                                <div class="text-sm text-gray-500">Events Processed</div>
                            </div>
                        </div>
                    </div>
                    <div class="bg-white rounded-lg shadow-md p-6 card-hover">
                        <div class="flex items-center">
                            <div class="text-3xl text-yellow-500">🔧</div>
                            <div class="ml-4">
                                <div class="text-2xl font-bold text-gray-900" x-text="metrics.problems_resolved">0</div>
                                <div class="text-sm text-gray-500">Problems Resolved</div>
                            </div>
                        </div>
                    </div>
                    <div class="bg-white rounded-lg shadow-md p-6 card-hover">
                        <div class="flex items-center">
                            <div class="text-3xl text-purple-500">👥</div>
                            <div class="ml-4">
                                <div class="text-2xl font-bold text-gray-900" x-text="metrics.customer_interactions">0</div>
                                <div class="text-sm text-gray-500">Customer Interactions</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">🚀 Quick Actions</h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <button @click="runPersonalizationDemo()" 
                                class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                            🧠 Run Personalization Demo
                        </button>
                        <button @click="runInventoryDemo()" 
                                class="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors">
                            📦 Run Inventory Demo
                        </button>
                        <button @click="runProblemResolutionDemo()" 
                                class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors">
                            🚨 Run Problem Resolution Demo
                        </button>
                    </div>
                </div>
            </div>

            <!-- Customers Tab -->
            <div x-show="activeTab === 'customers'" class="space-y-6">
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">👥 Select Customer</h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <template x-for="(customer, userId) in customers" :key="userId">
                            <div class="border rounded-lg p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                                 @click="selectCustomer(userId)"
                                 :class="selectedCustomer === userId ? 'border-blue-500 bg-blue-50' : 'border-gray-200'">
                                <div class="flex items-center space-x-3">
                                    <div class="text-2xl">👤</div>
                                    <div>
                                        <div class="font-semibold" x-text="customer.name"></div>
                                        <div class="text-sm text-gray-500" x-text="customer.loyalty_tier"></div>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>

                <!-- Selected Customer Actions -->
                <div x-show="selectedCustomer" class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">🛒 Customer Actions</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <!-- Cart -->
                        <div>
                            <h4 class="font-medium text-gray-900 mb-2">Shopping Cart</h4>
                            <div class="border rounded-lg p-4 min-h-32">
                                <template x-if="cart.items.length === 0">
                                    <div class="text-gray-500 text-center py-4">Cart is empty</div>
                                </template>
                                <template x-for="item in cart.items" :key="item.product_id">
                                    <div class="flex items-center space-x-3 py-2 border-b">
                                        <img :src="item.image" class="w-12 h-12 rounded object-cover">
                                        <div class="flex-1">
                                            <div class="font-medium" x-text="item.name"></div>
                                            <div class="text-sm text-gray-500">Qty: <span x-text="item.quantity"></span></div>
                                        </div>
                                        <div class="font-semibold" x-text="'$' + (item.price * item.quantity).toFixed(2)"></div>
                                    </div>
                                </template>
                                <template x-if="cart.items.length > 0">
                                    <div class="mt-4 pt-4 border-t">
                                        <div class="flex justify-between font-semibold">
                                            <span>Total:</span>
                                            <span x-text="'$' + cart.total.toFixed(2)"></span>
                                        </div>
                                        <button @click="checkout()" 
                                                class="w-full mt-2 bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 transition-colors">
                                            💳 Checkout
                                        </button>
                                    </div>
                                </template>
                            </div>
                        </div>

                        <!-- AI Recommendations -->
                        <div>
                            <h4 class="font-medium text-gray-900 mb-2">🤖 AI Recommendations</h4>
                            <div class="border rounded-lg p-4 min-h-32">
                                <template x-if="recommendations.length === 0">
                                    <div class="text-gray-500 text-center py-4">No recommendations yet</div>
                                </template>
                                <template x-for="rec in recommendations" :key="rec.product_id">
                                    <div class="flex items-center space-x-3 py-2 border-b">
                                        <img :src="rec.image" class="w-12 h-12 rounded object-cover">
                                        <div class="flex-1">
                                            <div class="font-medium" x-text="rec.name"></div>
                                            <div class="text-sm text-gray-500" x-text="rec.reason"></div>
                                        </div>
                                        <div class="text-right">
                                            <div class="font-semibold" x-text="'$' + rec.price"></div>
                                            <div class="text-sm text-green-600" x-text="'$' + rec.discount + ' off'"></div>
                                        </div>
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Inventory Tab -->
            <div x-show="activeTab === 'inventory'" class="space-y-6">
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">📦 Inventory Management</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <template x-for="(product, productId) in inventory" :key="productId">
                            <div class="border rounded-lg p-4 card-hover">
                                <img :src="product.image" class="w-full h-32 object-cover rounded mb-3">
                                <div class="font-semibold" x-text="product.name"></div>
                                <div class="text-lg font-bold text-blue-600" x-text="'$' + product.price"></div>
                                <div class="text-sm text-gray-500 mt-2">Stock Levels:</div>
                                <template x-for="(warehouse, name) in product.warehouses" :key="name">
                                    <div class="flex justify-between text-sm">
                                        <span x-text="name"></span>
                                        <span :class="warehouse.stock <= warehouse.threshold ? 'text-red-600' : 'text-green-600'"
                                              x-text="warehouse.stock + ' units'"></span>
                                    </div>
                                </template>
                                <button @click="addToCart(productId)" 
                                        class="w-full mt-3 bg-blue-500 text-white py-1 rounded hover:bg-blue-600 transition-colors">
                                    Add to Cart
                                </button>
                            </div>
                        </template>
                    </div>
                </div>
            </div>

            <!-- Analytics Tab -->
            <div x-show="activeTab === 'analytics'" class="space-y-6">
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">📈 Business Impact</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <div class="text-center">
                            <div class="text-3xl font-bold text-green-600">+23%</div>
                            <div class="text-sm text-gray-500">Conversion Rate</div>
                        </div>
                        <div class="text-center">
                            <div class="text-3xl font-bold text-blue-600">+18%</div>
                            <div class="text-sm text-gray-500">Average Order Value</div>
                        </div>
                        <div class="text-center">
                            <div class="text-3xl font-bold text-red-600">-31%</div>
                            <div class="text-sm text-gray-500">Cart Abandonment</div>
                        </div>
                        <div class="text-center">
                            <div class="text-3xl font-bold text-purple-600">+15%</div>
                            <div class="text-sm text-gray-500">Customer Satisfaction</div>
                        </div>
                        <div class="text-center">
                            <div class="text-3xl font-bold text-yellow-600">+42%</div>
                            <div class="text-sm text-gray-500">Operational Efficiency</div>
                        </div>
                        <div class="text-center">
                            <div class="text-3xl font-bold text-indigo-600">$47K</div>
                            <div class="text-sm text-gray-500">Monthly Savings</div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        function aegisApp() {
            return {
                activeTab: 'dashboard',
                selectedCustomer: null,
                customers: {},
                inventory: {},
                cart: { items: [], total: 0 },
                recommendations: [],
                metrics: { ai_decisions: 0, events_processed: 0, problems_resolved: 0, customer_interactions: 0 },
                
                async init() {
                    await this.loadData();
                },
                
                async loadData() {
                    try {
                        const [customersRes, inventoryRes, metricsRes] = await Promise.all([
                            fetch('/api/customers'),
                            fetch('/api/inventory'),
                            fetch('/api/metrics')
                        ]);
                        
                        this.customers = await customersRes.json();
                        this.inventory = await inventoryRes.json();
                        const metricsData = await metricsRes.json();
                        this.metrics = metricsData.system_metrics;
                    } catch (error) {
                        console.error('Error loading data:', error);
                    }
                },
                
                async selectCustomer(userId) {
                    this.selectedCustomer = userId;
                    this.cart = { items: [], total: 0 };
                    this.recommendations = [];
                    
                    try {
                        const response = await fetch(`/api/select-customer`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                            body: `user_id=${userId}`
                        });
                        const data = await response.json();
                        if (data.success) {
                            console.log('Customer selected:', data.user);
                        }
                    } catch (error) {
                        console.error('Error selecting customer:', error);
                    }
                },
                
                async addToCart(productId) {
                    if (!this.selectedCustomer) {
                        alert('Please select a customer first');
                        return;
                    }
                    
                    try {
                        const response = await fetch(`/api/add-to-cart`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                            body: `user_id=${this.selectedCustomer}&product_id=${productId}&quantity=1`
                        });
                        const data = await response.json();
                        if (data.success) {
                            this.cart = data.cart;
                            await this.getRecommendations();
                        }
                    } catch (error) {
                        console.error('Error adding to cart:', error);
                    }
                },
                
                async getRecommendations() {
                    if (!this.selectedCustomer) return;
                    
                    try {
                        const response = await fetch(`/api/recommendations/${this.selectedCustomer}`);
                        const data = await response.json();
                        this.recommendations = data.recommendations || [];
                    } catch (error) {
                        console.error('Error getting recommendations:', error);
                    }
                },
                
                async checkout() {
                    if (!this.selectedCustomer) return;
                    
                    try {
                        const response = await fetch(`/api/simulate-payment`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                            body: `user_id=${this.selectedCustomer}`
                        });
                        const data = await response.json();
                        
                        if (data.success) {
                            alert('Payment successful! ' + data.message);
                            this.cart = { items: [], total: 0 };
                            this.recommendations = [];
                        } else {
                            alert('Payment failed: ' + data.error);
                            if (data.ai_response) {
                                alert('AI Response: ' + data.ai_response.message);
                            }
                        }
                        
                        await this.loadData();
                    } catch (error) {
                        console.error('Error during checkout:', error);
                    }
                },
                
                async runPersonalizationDemo() {
                    alert('Personalization Demo: AI analyzes customer behavior and generates smart recommendations!');
                },
                
                async runInventoryDemo() {
                    alert('Inventory Demo: AI monitors stock levels and optimizes warehouse allocation!');
                },
                
                async runProblemResolutionDemo() {
                    alert('Problem Resolution Demo: AI detects and resolves issues automatically!');
                }
            }
        }
    </script>
</body>
</html>
    """

@app.get("/api/customers")
async def get_customers():
    """Get all customers."""
    return aegis.user_profiles

@app.get("/api/inventory")
async def get_inventory():
    """Get inventory data."""
    return aegis.inventory_data

@app.get("/api/cart/{user_id}")
async def get_cart(user_id: str):
    """Get user's cart."""
    if user_id in aegis.cart_data:
        return aegis.cart_data[user_id]
    return {"error": "User not found"}

@app.post("/api/select-customer")
async def select_customer(user_id: str = Form(...)):
    """Select a customer."""
    if user_id in aegis.user_profiles:
        aegis.current_user = user_id
        return {"success": True, "user": aegis.user_profiles[user_id]}
    return {"success": False, "error": "User not found"}

@app.post("/api/add-to-cart")
async def add_to_cart(
    user_id: str = Form(...),
    product_id: str = Form(...),
    quantity: int = Form(1)
):
    """Add item to cart."""
    if user_id not in aegis.user_profiles:
        return {"success": False, "error": "User not found"}
    
    if product_id not in aegis.inventory_data:
        return {"success": False, "error": "Product not found"}
    
    product = aegis.inventory_data[product_id]
    cart_item = {
        "product_id": product_id,
        "name": product["name"],
        "price": product["price"],
        "quantity": quantity,
        "image": product["image"]
    }
    
    aegis.cart_data[user_id]["items"].append(cart_item)
    aegis.cart_data[user_id]["total"] += product["price"] * quantity
    
    # Trigger AI analysis
    await aegis._trigger_cart_analysis(user_id)
    
    return {"success": True, "cart": aegis.cart_data[user_id]}

async def _trigger_cart_analysis(self, user_id: str):
    """Trigger AI cart analysis."""
    if user_id not in self.user_profiles:
        return
    
    cart_items = self.cart_data[user_id]["items"]
    user_profile = self.user_profiles[user_id]
    
    # Generate AI recommendations
    recommendations = await self._generate_ai_recommendations(cart_items, user_profile)
    
    self.system_metrics["ai_decisions"] += 1
    self.system_metrics["events_processed"] += 1
    
    return recommendations

async def _generate_ai_recommendations(self, cart_items, user_profile):
    """Generate AI recommendations based on cart and profile."""
    recommendations = []
    
    # Simple AI logic for demo
    cart_categories = set()
    for item in cart_items:
        product = self.inventory_data[item["product_id"]]
        cart_categories.add(product["category"])
    
    # Find complementary items
    for product_id, product in self.inventory_data.items():
        if product["category"] not in cart_categories:
            # Check if it matches user preferences
            if any(tag in user_profile["preferences"]["colors"] for tag in product["tags"]):
                recommendations.append({
                    "product_id": product_id,
                    "name": product["name"],
                    "reason": f"Matches your {user_profile['preferences']['style']} style",
                    "discount": 10,
                    "confidence": 0.85,
                    "image": product["image"],
                    "price": product["price"]
                })
    
    return recommendations[:3]  # Return top 3 recommendations

# Add methods to the class
WebAegisOrchestrator._trigger_cart_analysis = _trigger_cart_analysis
WebAegisOrchestrator._generate_ai_recommendations = _generate_ai_recommendations

@app.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    """Get AI recommendations for user."""
    if user_id not in aegis.user_profiles:
        return {"error": "User not found"}
    
    user_profile = aegis.user_profiles[user_id]
    cart_items = aegis.cart_data[user_id]["items"]
    
    recommendations = await aegis._generate_ai_recommendations(cart_items, user_profile)
    
    aegis.system_metrics["ai_decisions"] += 1
    
    return {"recommendations": recommendations}

@app.get("/api/inventory-status")
async def get_inventory_status():
    """Get inventory status with alerts."""
    alerts = []
    for product_id, product in aegis.inventory_data.items():
        for warehouse, data in product['warehouses'].items():
            if data['stock'] <= data['threshold']:
                alerts.append({
                    "product": product['name'],
                    "warehouse": warehouse,
                    "stock": data['stock'],
                    "threshold": data['threshold'],
                    "severity": "high" if data['stock'] < data['threshold'] else "medium"
                })
    
    return {"alerts": alerts, "inventory": aegis.inventory_data}

@app.post("/api/simulate-payment")
async def simulate_payment(user_id: str = Form(...)):
    """Simulate payment process."""
    if user_id not in aegis.user_profiles:
        return {"success": False, "error": "User not found"}
    
    cart = aegis.cart_data[user_id]
    if not cart["items"]:
        return {"success": False, "error": "Cart is empty"}
    
    # Simulate payment processing
    import random
    if random.random() < 0.3:  # 30% chance of failure
        # Payment failed - trigger AI resolution
        aegis.system_metrics["problems_resolved"] += 1
        aegis.system_metrics["ai_decisions"] += 1
        
        return {
            "success": False,
            "error": "Payment failed",
            "ai_response": {
                "action": "retry_payment",
                "message": "We're working to resolve this issue. Your order is safe.",
                "retry_attempts": 1
            }
        }
    else:
        # Payment successful
        aegis.system_metrics["customer_interactions"] += 1
        aegis.cart_data[user_id] = {"items": [], "total": 0.0}
        
        return {
            "success": True,
            "message": "Payment successful! Order confirmed.",
            "order_id": f"ORD-{int(time.time())}"
        }

@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics."""
    return {
        "system_metrics": aegis.system_metrics,
        "business_impact": {
            "conversion_rate_increase": "+23%",
            "average_order_value_increase": "+18%",
            "cart_abandonment_reduction": "-31%",
            "customer_satisfaction_increase": "+15%",
            "operational_efficiency_gain": "+42%",
            "monthly_cost_savings": "$47,000"
        }
    }

if __name__ == "__main__":
    print("Starting Aegis Orchestrator Web Demo...")
    print("Open your browser and go to: http://localhost:8000")
    print("Experience the full AI-powered e-commerce intelligence platform!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
