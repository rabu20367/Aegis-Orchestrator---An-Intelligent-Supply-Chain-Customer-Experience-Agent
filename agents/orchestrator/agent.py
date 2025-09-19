"""Orchestrator Agent - Central coordination agent for Aegis Orchestrator."""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
import google.generativeai as genai

from agents.base_agent import BaseAgent, AgentMessage, AgentResponse
from config.settings import settings


class OrchestratorAgent(BaseAgent):
    """Central orchestrator agent that coordinates all other agents."""
    
    def __init__(self):
        super().__init__(
            agent_id="orchestrator",
            agent_name="orchestrator"
        )
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        
        # Agent registry
        self.agents = {
            "personalization": "personalization-agent",
            "inventory": "inventory-agent", 
            "customer_comms": "customer-comms-agent",
            "anomaly_resolver": "anomaly-resolver-agent"
        }
        
        # Event handlers
        self.event_handlers = {
            "order_created": self._handle_order_created,
            "cart_updated": self._handle_cart_updated,
            "inventory_low": self._handle_inventory_low,
            "payment_failed": self._handle_payment_failed,
            "shipping_delayed": self._handle_shipping_delayed,
            "user_browsing": self._handle_user_browsing
        }
    
    async def initialize(self):
        """Initialize the orchestrator agent."""
        self.logger.info("Initializing Orchestrator Agent")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("Orchestrator Agent initialized")
    
    async def cleanup(self):
        """Cleanup orchestrator resources."""
        self.logger.info("Cleaning up Orchestrator Agent")
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentResponse]:
        """Handle incoming messages from other agents."""
        try:
            message_type = message.message_type
            content = message.content
            
            self.logger.info(f"Handling message type: {message_type}")
            
            if message_type == "event":
                return await self._handle_event(content)
            elif message_type == "request":
                return await self._handle_request(content)
            elif message_type == "response":
                return await self._handle_response(content)
            else:
                self.logger.warning(f"Unknown message type: {message_type}")
                return AgentResponse(success=False, error=f"Unknown message type: {message_type}")
                
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            return AgentResponse(success=False, error=str(e))
    
    async def _handle_event(self, event_data: Dict[str, Any]) -> AgentResponse:
        """Handle system events."""
        event_type = event_data.get("event_type")
        
        if event_type in self.event_handlers:
            try:
                result = await self.event_handlers[event_type](event_data)
                return AgentResponse(success=True, data=result)
            except Exception as e:
                self.logger.error(f"Error handling event {event_type}: {e}")
                return AgentResponse(success=False, error=str(e))
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
            return AgentResponse(success=False, error=f"Unknown event type: {event_type}")
    
    async def _handle_request(self, request_data: Dict[str, Any]) -> AgentResponse:
        """Handle requests from other agents."""
        request_type = request_data.get("request_type")
        
        if request_type == "coordinate_agents":
            return await self._coordinate_agents(request_data)
        elif request_type == "analyze_situation":
            return await self._analyze_situation(request_data)
        else:
            return AgentResponse(success=False, error=f"Unknown request type: {request_type}")
    
    async def _handle_response(self, response_data: Dict[str, Any]) -> AgentResponse:
        """Handle responses from other agents."""
        # Log the response for monitoring
        self.logger.info(f"Received response: {response_data}")
        return AgentResponse(success=True)
    
    async def _monitoring_loop(self):
        """Main monitoring loop for system health and events."""
        while self.is_running:
            try:
                # Check system health
                await self._check_system_health()
                
                # Process any pending events
                await self._process_pending_events()
                
                # Wait before next check
                await asyncio.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _check_system_health(self):
        """Check the health of all agents and services."""
        # This would check the health of all registered agents
        # For now, we'll just log that we're checking
        self.logger.debug("Checking system health")
    
    async def _process_pending_events(self):
        """Process any pending system events."""
        # This would process events from the event queue
        # For now, we'll just log that we're processing
        self.logger.debug("Processing pending events")
    
    # Event Handlers
    async def _handle_order_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new order creation."""
        order_id = event_data.get("order_id")
        user_id = event_data.get("user_id")
        
        self.logger.info(f"Handling new order {order_id} for user {user_id}")
        
        # Get order details
        order = await self.get_order(order_id)
        
        # Coordinate agents for order processing
        tasks = []
        
        # Notify inventory agent to update stock
        tasks.append(self._notify_agent("inventory", "event", {
            "event_type": "order_created",
            "order_id": order_id,
            "order_data": order
        }))
        
        # Notify customer comms agent to send confirmation
        tasks.append(self._notify_agent("customer_comms", "event", {
            "event_type": "order_created",
            "order_id": order_id,
            "user_id": user_id,
            "order_data": order
        }))
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return {"status": "order_processing_initiated", "order_id": order_id}
    
    async def _handle_cart_updated(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cart updates."""
        user_id = event_data.get("user_id")
        cart_data = event_data.get("cart_data")
        
        self.logger.info(f"Handling cart update for user {user_id}")
        
        # Notify personalization agent for recommendations
        await self._notify_agent("personalization", "event", {
            "event_type": "cart_updated",
            "user_id": user_id,
            "cart_data": cart_data
        })
        
        return {"status": "cart_analysis_initiated", "user_id": user_id}
    
    async def _handle_inventory_low(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle low inventory alerts."""
        product_id = event_data.get("product_id")
        current_stock = event_data.get("current_stock")
        
        self.logger.warning(f"Low inventory alert for product {product_id}: {current_stock} units")
        
        # Notify anomaly resolver to handle the situation
        await self._notify_agent("anomaly_resolver", "event", {
            "event_type": "inventory_low",
            "product_id": product_id,
            "current_stock": current_stock
        })
        
        return {"status": "inventory_issue_escalated", "product_id": product_id}
    
    async def _handle_payment_failed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment failures."""
        order_id = event_data.get("order_id")
        user_id = event_data.get("user_id")
        error_reason = event_data.get("error_reason")
        
        self.logger.error(f"Payment failed for order {order_id}: {error_reason}")
        
        # Notify anomaly resolver to handle the payment issue
        await self._notify_agent("anomaly_resolver", "event", {
            "event_type": "payment_failed",
            "order_id": order_id,
            "user_id": user_id,
            "error_reason": error_reason
        })
        
        return {"status": "payment_issue_escalated", "order_id": order_id}
    
    async def _handle_shipping_delayed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle shipping delays."""
        order_id = event_data.get("order_id")
        user_id = event_data.get("user_id")
        delay_reason = event_data.get("delay_reason")
        
        self.logger.warning(f"Shipping delay for order {order_id}: {delay_reason}")
        
        # Notify customer comms agent to inform the customer
        await self._notify_agent("customer_comms", "event", {
            "event_type": "shipping_delayed",
            "order_id": order_id,
            "user_id": user_id,
            "delay_reason": delay_reason
        })
        
        return {"status": "customer_notified", "order_id": order_id}
    
    async def _handle_user_browsing(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user browsing events."""
        user_id = event_data.get("user_id")
        page = event_data.get("page")
        products_viewed = event_data.get("products_viewed", [])
        
        self.logger.info(f"User {user_id} browsing {page}, viewed {len(products_viewed)} products")
        
        # Notify personalization agent for recommendations
        await self._notify_agent("personalization", "event", {
            "event_type": "user_browsing",
            "user_id": user_id,
            "page": page,
            "products_viewed": products_viewed
        })
        
        return {"status": "browsing_analyzed", "user_id": user_id}
    
    async def _coordinate_agents(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate multiple agents for a complex task."""
        task_type = request_data.get("task_type")
        parameters = request_data.get("parameters", {})
        
        self.logger.info(f"Coordinating agents for task: {task_type}")
        
        if task_type == "personalized_checkout":
            return await self._coordinate_personalized_checkout(parameters)
        elif task_type == "inventory_optimization":
            return await self._coordinate_inventory_optimization(parameters)
        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}
    
    async def _coordinate_personalized_checkout(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate agents for personalized checkout experience."""
        user_id = parameters.get("user_id")
        cart_data = parameters.get("cart_data")
        
        # Get personalization recommendations
        personalization_response = await self._notify_agent("personalization", "request", {
            "request_type": "get_recommendations",
            "user_id": user_id,
            "cart_data": cart_data
        })
        
        # Get inventory status for recommended items
        inventory_response = await self._notify_agent("inventory", "request", {
            "request_type": "check_availability",
            "product_ids": personalization_response.get("recommended_products", [])
        })
        
        return {
            "status": "coordination_complete",
            "personalization": personalization_response,
            "inventory": inventory_response
        }
    
    async def _coordinate_inventory_optimization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate agents for inventory optimization."""
        # This would coordinate inventory and anomaly resolver agents
        # to optimize stock levels and handle issues
        return {"status": "inventory_optimization_initiated"}
    
    async def _analyze_situation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Gemini to analyze complex situations and make decisions."""
        situation_description = request_data.get("situation_description")
        context_data = request_data.get("context_data", {})
        
        # Create a prompt for Gemini
        prompt = f"""
        As the Aegis Orchestrator, analyze this situation and provide recommendations:
        
        Situation: {situation_description}
        Context: {context_data}
        
        Please provide:
        1. Analysis of the situation
        2. Recommended actions
        3. Which agents should be involved
        4. Expected outcomes
        
        Respond in JSON format.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            analysis = response.text
            
            # Parse the response (in a real implementation, you'd want better parsing)
            return {
                "status": "analysis_complete",
                "analysis": analysis,
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.error(f"Error analyzing situation with Gemini: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _notify_agent(self, agent_type: str, message_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification to a specific agent."""
        agent_id = self.agents.get(agent_type)
        if not agent_id:
            self.logger.error(f"Unknown agent type: {agent_type}")
            return {"status": "error", "message": f"Unknown agent type: {agent_type}"}
        
        try:
            await self.send_message(agent_id, message_type, content)
            return {"status": "notification_sent", "agent": agent_type}
        except Exception as e:
            self.logger.error(f"Failed to notify agent {agent_type}: {e}")
            return {"status": "error", "message": str(e)}
