"""Inventory Agent - Predictive inventory management and optimization."""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
import google.generativeai as genai
import numpy as np
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent, AgentMessage, AgentResponse
from config.settings import settings


class InventoryAgent(BaseAgent):
    """AI-powered inventory management agent for stock optimization and demand prediction."""
    
    def __init__(self):
        super().__init__(
            agent_id="inventory-agent",
            agent_name="inventory"
        )
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        
        # Inventory tracking
        self.inventory_levels = {}
        self.demand_predictions = {}
        self.warehouse_locations = ["east-coast", "west-coast", "central"]
        self.reorder_thresholds = {}
        self.supply_chain_status = {}
        
        # Historical data for predictions
        self.sales_history = {}
        self.seasonal_patterns = {}
        
    async def initialize(self):
        """Initialize the inventory agent."""
        self.logger.info("Initializing Inventory Agent")
        
        # Load current inventory levels
        await self._load_inventory_levels()
        
        # Start monitoring tasks
        asyncio.create_task(self._monitor_inventory_levels())
        asyncio.create_task(self._update_demand_predictions())
        asyncio.create_task(self._check_supply_chain_health())
        
        self.logger.info("Inventory Agent initialized")
    
    async def cleanup(self):
        """Cleanup inventory resources."""
        self.logger.info("Cleaning up Inventory Agent")
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentResponse]:
        """Handle incoming messages."""
        try:
            message_type = message.message_type
            content = message.content
            
            if message_type == "event":
                return await self._handle_event(content)
            elif message_type == "request":
                return await self._handle_request(content)
            else:
                return AgentResponse(success=False, error=f"Unknown message type: {message_type}")
                
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            return AgentResponse(success=False, error=str(e))
    
    async def _handle_event(self, event_data: Dict[str, Any]) -> AgentResponse:
        """Handle inventory events."""
        event_type = event_data.get("event_type")
        
        if event_type == "order_created":
            return await self._handle_order_created(event_data)
        elif event_type == "inventory_low":
            return await self._handle_inventory_low(event_data)
        elif event_type == "supply_chain_disruption":
            return await self._handle_supply_chain_disruption(event_data)
        else:
            return AgentResponse(success=False, error=f"Unknown event type: {event_type}")
    
    async def _handle_request(self, request_data: Dict[str, Any]) -> AgentResponse:
        """Handle inventory requests."""
        request_type = request_data.get("request_type")
        
        if request_type == "check_availability":
            return await self._check_availability(request_data)
        elif request_type == "predict_demand":
            return await self._predict_demand(request_data)
        elif request_type == "optimize_inventory":
            return await self._optimize_inventory(request_data)
        elif request_type == "get_reorder_suggestions":
            return await self._get_reorder_suggestions(request_data)
        else:
            return AgentResponse(success=False, error=f"Unknown request type: {request_type}")
    
    async def _handle_order_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new order creation - update inventory levels."""
        order_id = event_data.get("order_id")
        order_data = event_data.get("order_data")
        
        self.logger.info(f"Processing order {order_id} for inventory update")
        
        # Extract order items
        order_items = order_data.get("items", [])
        
        # Update inventory levels
        for item in order_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 0)
            
            if product_id:
                await self._update_inventory_level(product_id, -quantity)
                
                # Check if inventory is now low
                current_level = self.inventory_levels.get(product_id, {}).get("total", 0)
                if current_level <= self.reorder_thresholds.get(product_id, 10):
                    await self._trigger_low_inventory_alert(product_id, current_level)
        
        return {
            "status": "inventory_updated",
            "order_id": order_id,
            "items_processed": len(order_items)
        }
    
    async def _handle_inventory_low(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle low inventory alerts."""
        product_id = event_data.get("product_id")
        current_stock = event_data.get("current_stock")
        
        self.logger.warning(f"Low inventory alert for product {product_id}: {current_stock} units")
        
        # Generate reorder suggestions
        reorder_suggestions = await self._generate_reorder_suggestions(product_id)
        
        # Notify orchestrator about the issue
        await self.send_message("orchestrator", "event", {
            "event_type": "inventory_critical",
            "product_id": product_id,
            "current_stock": current_stock,
            "reorder_suggestions": reorder_suggestions
        })
        
        return {
            "status": "low_inventory_handled",
            "product_id": product_id,
            "reorder_suggestions": reorder_suggestions
        }
    
    async def _handle_supply_chain_disruption(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle supply chain disruptions."""
        disruption_type = event_data.get("disruption_type")
        affected_products = event_data.get("affected_products", [])
        estimated_duration = event_data.get("estimated_duration")
        
        self.logger.warning(f"Supply chain disruption: {disruption_type} affecting {len(affected_products)} products")
        
        # Update supply chain status
        self.supply_chain_status[disruption_type] = {
            "affected_products": affected_products,
            "estimated_duration": estimated_duration,
            "start_time": time.time()
        }
        
        # Generate mitigation strategies
        mitigation_strategies = await self._generate_mitigation_strategies(disruption_type, affected_products)
        
        return {
            "status": "disruption_handled",
            "disruption_type": disruption_type,
            "mitigation_strategies": mitigation_strategies
        }
    
    async def _check_availability(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check product availability across warehouses."""
        product_ids = request_data.get("product_ids", [])
        
        availability = {}
        for product_id in product_ids:
            product_availability = await self._get_product_availability(product_id)
            availability[product_id] = product_availability
        
        return {
            "status": "availability_checked",
            "availability": availability
        }
    
    async def _predict_demand(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict demand for products using AI."""
        product_id = request_data.get("product_id")
        time_horizon = request_data.get("time_horizon", 7)  # days
        
        if product_id:
            prediction = await self._generate_demand_prediction(product_id, time_horizon)
            return {
                "status": "demand_predicted",
                "product_id": product_id,
                "prediction": prediction
            }
        else:
            # Predict for all products
            predictions = {}
            for pid in self.inventory_levels.keys():
                predictions[pid] = await self._generate_demand_prediction(pid, time_horizon)
            
            return {
                "status": "demand_predicted",
                "predictions": predictions
            }
    
    async def _optimize_inventory(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize inventory levels using AI."""
        optimization_goals = request_data.get("goals", ["minimize_costs", "maximize_availability"])
        
        # Use Gemini to analyze current inventory and suggest optimizations
        prompt = f"""
        As an inventory optimization AI, analyze the current inventory levels and suggest optimizations:
        
        Current Inventory: {self.inventory_levels}
        Reorder Thresholds: {self.reorder_thresholds}
        Optimization Goals: {optimization_goals}
        
        Please provide:
        1. Products that need reordering
        2. Suggested reorder quantities
        3. Warehouse distribution recommendations
        4. Cost optimization opportunities
        5. Risk assessments
        
        Respond in JSON format.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            optimization_plan = self._parse_optimization_plan(response.text)
            
            return {
                "status": "inventory_optimized",
                "optimization_plan": optimization_plan
            }
        except Exception as e:
            self.logger.error(f"Error optimizing inventory: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _get_reorder_suggestions(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get reorder suggestions for low-stock items."""
        suggestions = []
        
        for product_id, inventory_data in self.inventory_levels.items():
            current_stock = inventory_data.get("total", 0)
            threshold = self.reorder_thresholds.get(product_id, 10)
            
            if current_stock <= threshold:
                suggestion = await self._generate_reorder_suggestion(product_id, current_stock, threshold)
                suggestions.append(suggestion)
        
        return {
            "status": "reorder_suggestions_generated",
            "suggestions": suggestions
        }
    
    async def _load_inventory_levels(self):
        """Load current inventory levels from the system."""
        try:
            # Get all products
            products = await self.get_products()
            
            # Initialize inventory levels (in production, this would come from a database)
            for product in products:
                product_id = product.get("id")
                if product_id:
                    self.inventory_levels[product_id] = {
                        "total": np.random.randint(50, 200),  # Mock data
                        "east-coast": np.random.randint(10, 50),
                        "west-coast": np.random.randint(10, 50),
                        "central": np.random.randint(10, 50),
                        "last_updated": time.time()
                    }
                    
                    # Set reorder threshold
                    self.reorder_thresholds[product_id] = 20
            
            self.logger.info(f"Loaded inventory levels for {len(self.inventory_levels)} products")
            
        except Exception as e:
            self.logger.error(f"Error loading inventory levels: {e}")
    
    async def _monitor_inventory_levels(self):
        """Background task to monitor inventory levels."""
        while self.is_running:
            try:
                # Check for low inventory items
                for product_id, inventory_data in self.inventory_levels.items():
                    current_stock = inventory_data.get("total", 0)
                    threshold = self.reorder_thresholds.get(product_id, 10)
                    
                    if current_stock <= threshold:
                        await self._trigger_low_inventory_alert(product_id, current_stock)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error monitoring inventory: {e}")
                await asyncio.sleep(60)
    
    async def _update_demand_predictions(self):
        """Background task to update demand predictions."""
        while self.is_running:
            try:
                # Update demand predictions for all products
                for product_id in self.inventory_levels.keys():
                    prediction = await self._generate_demand_prediction(product_id, 7)
                    self.demand_predictions[product_id] = prediction
                
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                self.logger.error(f"Error updating demand predictions: {e}")
                await asyncio.sleep(300)
    
    async def _check_supply_chain_health(self):
        """Background task to check supply chain health."""
        while self.is_running:
            try:
                # Check for supply chain disruptions
                # This would integrate with real supply chain monitoring systems
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Error checking supply chain: {e}")
                await asyncio.sleep(300)
    
    async def _update_inventory_level(self, product_id: str, quantity_change: int):
        """Update inventory level for a product."""
        if product_id in self.inventory_levels:
            current_total = self.inventory_levels[product_id].get("total", 0)
            new_total = max(0, current_total + quantity_change)
            
            self.inventory_levels[product_id]["total"] = new_total
            self.inventory_levels[product_id]["last_updated"] = time.time()
            
            self.logger.info(f"Updated inventory for {product_id}: {current_total} -> {new_total}")
    
    async def _trigger_low_inventory_alert(self, product_id: str, current_stock: int):
        """Trigger low inventory alert."""
        await self.send_message("orchestrator", "event", {
            "event_type": "inventory_low",
            "product_id": product_id,
            "current_stock": current_stock,
            "threshold": self.reorder_thresholds.get(product_id, 10)
        })
    
    async def _get_product_availability(self, product_id: str) -> Dict[str, Any]:
        """Get product availability across warehouses."""
        inventory_data = self.inventory_levels.get(product_id, {})
        
        return {
            "product_id": product_id,
            "total_available": inventory_data.get("total", 0),
            "warehouse_availability": {
                warehouse: inventory_data.get(warehouse, 0)
                for warehouse in self.warehouse_locations
            },
            "last_updated": inventory_data.get("last_updated", 0)
        }
    
    async def _generate_demand_prediction(self, product_id: str, time_horizon: int) -> Dict[str, Any]:
        """Generate demand prediction using AI."""
        try:
            # Get historical data
            historical_data = self.sales_history.get(product_id, [])
            current_inventory = self.inventory_levels.get(product_id, {}).get("total", 0)
            
            # Use Gemini to predict demand
            prompt = f"""
            As a demand forecasting AI, predict demand for this product:
            
            Product ID: {product_id}
            Time Horizon: {time_horizon} days
            Current Inventory: {current_inventory}
            Historical Sales: {historical_data[-10:] if historical_data else "No data"}
            
            Consider:
            1. Seasonal patterns
            2. Historical trends
            3. Current inventory levels
            4. Market conditions
            5. Product lifecycle stage
            
            Respond with JSON containing:
            - predicted_demand (array of daily predictions)
            - confidence_score (0-1)
            - risk_factors
            - recommendations
            """
            
            response = await self.model.generate_content_async(prompt)
            prediction = self._parse_demand_prediction(response.text, time_horizon)
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error generating demand prediction: {e}")
            return {
                "predicted_demand": [0] * time_horizon,
                "confidence_score": 0.0,
                "risk_factors": ["Prediction error"],
                "recommendations": ["Manual review required"]
            }
    
    async def _generate_reorder_suggestion(self, product_id: str, current_stock: int, threshold: int) -> Dict[str, Any]:
        """Generate reorder suggestion for a product."""
        try:
            # Get demand prediction
            demand_prediction = await self._generate_demand_prediction(product_id, 14)
            predicted_demand = demand_prediction.get("predicted_demand", [0] * 14)
            avg_daily_demand = sum(predicted_demand) / len(predicted_demand) if predicted_demand else 1
            
            # Calculate reorder quantity
            lead_time_days = 7  # Assume 7-day lead time
            safety_stock = avg_daily_demand * 3  # 3 days of safety stock
            reorder_quantity = int((avg_daily_demand * lead_time_days) + safety_stock - current_stock)
            
            return {
                "product_id": product_id,
                "current_stock": current_stock,
                "reorder_quantity": max(0, reorder_quantity),
                "estimated_daily_demand": avg_daily_demand,
                "lead_time_days": lead_time_days,
                "safety_stock": safety_stock,
                "urgency": "high" if current_stock <= threshold else "medium"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating reorder suggestion: {e}")
            return {
                "product_id": product_id,
                "current_stock": current_stock,
                "reorder_quantity": 50,  # Default reorder quantity
                "urgency": "high"
            }
    
    async def _generate_mitigation_strategies(self, disruption_type: str, affected_products: List[str]) -> List[Dict[str, Any]]:
        """Generate mitigation strategies for supply chain disruptions."""
        try:
            prompt = f"""
            As a supply chain AI, suggest mitigation strategies for this disruption:
            
            Disruption Type: {disruption_type}
            Affected Products: {affected_products}
            
            Suggest strategies for:
            1. Alternative suppliers
            2. Inventory redistribution
            3. Customer communication
            4. Temporary substitutions
            5. Cost management
            
            Respond with JSON array of mitigation strategies.
            """
            
            response = await self.model.generate_content_async(prompt)
            strategies = self._parse_mitigation_strategies(response.text)
            
            return strategies
            
        except Exception as e:
            self.logger.error(f"Error generating mitigation strategies: {e}")
            return [{"strategy": "Manual intervention required", "priority": "high"}]
    
    def _parse_demand_prediction(self, response_text: str, time_horizon: int) -> Dict[str, Any]:
        """Parse AI response into demand prediction format."""
        try:
            # Mock prediction data
            predicted_demand = [np.random.randint(5, 20) for _ in range(time_horizon)]
            
            return {
                "predicted_demand": predicted_demand,
                "confidence_score": 0.8,
                "risk_factors": ["Seasonal variation", "Supply chain uncertainty"],
                "recommendations": ["Monitor closely", "Prepare for demand spikes"]
            }
        except Exception as e:
            self.logger.error(f"Error parsing demand prediction: {e}")
            return {
                "predicted_demand": [0] * time_horizon,
                "confidence_score": 0.0,
                "risk_factors": ["Parsing error"],
                "recommendations": ["Manual review required"]
            }
    
    def _parse_optimization_plan(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into optimization plan format."""
        try:
            # Mock optimization plan
            return {
                "reorder_products": ["product1", "product2"],
                "reorder_quantities": {"product1": 100, "product2": 150},
                "warehouse_distribution": {
                    "product1": {"east-coast": 40, "west-coast": 60},
                    "product2": {"central": 100}
                },
                "cost_savings": 2500.00,
                "risk_assessment": "Low risk"
            }
        except Exception as e:
            self.logger.error(f"Error parsing optimization plan: {e}")
            return {"error": "Failed to parse optimization plan"}
    
    def _parse_mitigation_strategies(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse AI response into mitigation strategies format."""
        try:
            # Mock mitigation strategies
            return [
                {
                    "strategy": "Activate backup suppliers",
                    "priority": "high",
                    "estimated_impact": "High",
                    "implementation_time": "2-3 days"
                },
                {
                    "strategy": "Redistribute inventory from other warehouses",
                    "priority": "medium",
                    "estimated_impact": "Medium",
                    "implementation_time": "1 day"
                }
            ]
        except Exception as e:
            self.logger.error(f"Error parsing mitigation strategies: {e}")
            return [{"strategy": "Manual intervention required", "priority": "high"}]
