"""Customer Communications Agent - AI-powered customer communication."""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent, AgentMessage, AgentResponse
from config.settings import settings


class CustomerCommsAgent(BaseAgent):
    """AI-powered customer communication agent for proactive and contextual messaging."""
    
    def __init__(self):
        super().__init__(
            agent_id="customer-comms-agent",
            agent_name="customer_comms"
        )
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        
        # Communication templates and preferences
        self.communication_templates = {}
        self.user_preferences = {}
        self.communication_history = {}
        
        # Message types and their handlers
        self.message_handlers = {
            "order_created": self._handle_order_created,
            "shipping_delayed": self._handle_shipping_delayed,
            "payment_failed": self._handle_payment_failed,
            "inventory_low": self._handle_inventory_low
        }
        
    async def initialize(self):
        """Initialize the customer communications agent."""
        self.logger.info("Initializing Customer Communications Agent")
        
        # Load communication templates
        await self._load_communication_templates()
        
        # Start background tasks
        asyncio.create_task(self._process_communication_queue())
        asyncio.create_task(self._cleanup_old_communications())
        
        self.logger.info("Customer Communications Agent initialized")
    
    async def cleanup(self):
        """Cleanup customer communications resources."""
        self.logger.info("Cleaning up Customer Communications Agent")
    
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
        """Handle communication events."""
        event_type = event_data.get("event_type")
        
        if event_type == "order_created":
            return await self._handle_order_created(event_data)
        elif event_type == "shipping_delayed":
            return await self._handle_shipping_delayed(event_data)
        elif event_type == "payment_failed":
            return await self._handle_payment_failed(event_data)
        elif event_type == "inventory_low":
            return await self._handle_inventory_low(event_data)
        else:
            return AgentResponse(success=False, error=f"Unknown event type: {event_type}")
    
    async def _handle_request(self, request_data: Dict[str, Any]) -> AgentResponse:
        """Handle communication requests."""
        request_type = request_data.get("request_type")
        
        if request_type == "send_message":
            return await self._send_custom_message(request_data)
        elif request_type == "get_communication_history":
            return await self._get_communication_history(request_data)
        elif request_type == "update_user_preferences":
            return await self._update_user_preferences(request_data)
        else:
            return AgentResponse(success=False, error=f"Unknown request type: {request_type}")
    
    async def _handle_order_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle order creation - send confirmation message."""
        order_id = event_data.get("order_id")
        user_id = event_data.get("user_id")
        order_data = event_data.get("order_data")
        
        self.logger.info(f"Sending order confirmation for order {order_id}")
        
        # Generate personalized confirmation message
        message = await self._generate_order_confirmation_message(user_id, order_data)
        
        # Send the message
        await self._send_message_to_customer(user_id, "order_confirmation", message, {
            "order_id": order_id,
            "order_data": order_data
        })
        
        return {
            "status": "confirmation_sent",
            "order_id": order_id,
            "user_id": user_id
        }
    
    async def _handle_shipping_delayed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle shipping delays - send proactive notification."""
        order_id = event_data.get("order_id")
        user_id = event_data.get("user_id")
        delay_reason = event_data.get("delay_reason")
        
        self.logger.info(f"Sending delay notification for order {order_id}")
        
        # Generate empathetic delay notification
        message = await self._generate_delay_notification_message(user_id, order_id, delay_reason)
        
        # Send the message
        await self._send_message_to_customer(user_id, "delay_notification", message, {
            "order_id": order_id,
            "delay_reason": delay_reason
        })
        
        return {
            "status": "delay_notification_sent",
            "order_id": order_id,
            "user_id": user_id
        }
    
    async def _handle_payment_failed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment failures - send helpful resolution message."""
        order_id = event_data.get("order_id")
        user_id = event_data.get("user_id")
        error_reason = event_data.get("error_reason")
        
        self.logger.info(f"Sending payment failure resolution for order {order_id}")
        
        # Generate helpful resolution message
        message = await self._generate_payment_failure_message(user_id, order_id, error_reason)
        
        # Send the message
        await self._send_message_to_customer(user_id, "issue_resolution", message, {
            "order_id": order_id,
            "issue_type": "payment_failed",
            "error_reason": error_reason
        })
        
        return {
            "status": "resolution_sent",
            "order_id": order_id,
            "user_id": user_id
        }
    
    async def _handle_inventory_low(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inventory issues - send proactive communication."""
        product_id = event_data.get("product_id")
        current_stock = event_data.get("current_stock")
        
        self.logger.info(f"Handling inventory low communication for product {product_id}")
        
        # Get users who have this product in their cart or wishlist
        affected_users = await self._get_affected_users(product_id)
        
        # Send proactive notifications
        for user_id in affected_users:
            message = await self._generate_inventory_alert_message(user_id, product_id, current_stock)
            await self._send_message_to_customer(user_id, "inventory_alert", message, {
                "product_id": product_id,
                "current_stock": current_stock
            })
        
        return {
            "status": "inventory_alerts_sent",
            "product_id": product_id,
            "affected_users": len(affected_users)
        }
    
    async def _send_custom_message(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a custom message to a customer."""
        user_id = request_data.get("user_id")
        message_type = request_data.get("message_type")
        content = request_data.get("content")
        context = request_data.get("context", {})
        
        # Generate personalized message
        message = await self._generate_custom_message(user_id, message_type, content, context)
        
        # Send the message
        await self._send_message_to_customer(user_id, message_type, message, context)
        
        return {
            "status": "custom_message_sent",
            "user_id": user_id,
            "message_type": message_type
        }
    
    async def _get_communication_history(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get communication history for a user."""
        user_id = request_data.get("user_id")
        limit = request_data.get("limit", 10)
        
        history = self.communication_history.get(user_id, [])
        
        return {
            "status": "history_retrieved",
            "user_id": user_id,
            "communications": history[-limit:]
        }
    
    async def _update_user_preferences(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user communication preferences."""
        user_id = request_data.get("user_id")
        preferences = request_data.get("preferences", {})
        
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        self.user_preferences[user_id].update(preferences)
        
        return {
            "status": "preferences_updated",
            "user_id": user_id,
            "preferences": self.user_preferences[user_id]
        }
    
    async def _load_communication_templates(self):
        """Load communication templates."""
        self.communication_templates = {
            "order_confirmation": {
                "subject": "Order Confirmation - {order_id}",
                "template": "Thank you for your order! We're excited to get your items ready for you."
            },
            "shipping_update": {
                "subject": "Your Order is on the Way!",
                "template": "Great news! Your order has been shipped and is on its way to you."
            },
            "delay_notification": {
                "subject": "Update on Your Order",
                "template": "We wanted to update you on your order status."
            },
            "payment_failed": {
                "subject": "Payment Issue - Let's Get This Sorted",
                "template": "We encountered an issue with your payment, but don't worry - we're here to help!"
            },
            "inventory_alert": {
                "subject": "Popular Item - Limited Stock",
                "template": "This popular item is running low on stock. Don't miss out!"
            }
        }
    
    async def _process_communication_queue(self):
        """Background task to process communication queue."""
        while self.is_running:
            try:
                # Process any pending communications
                # This would handle queued messages, retries, etc.
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error processing communication queue: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_communications(self):
        """Background task to cleanup old communications."""
        while self.is_running:
            try:
                # Clean up communications older than 30 days
                cutoff_time = time.time() - (30 * 24 * 60 * 60)
                
                for user_id, communications in self.communication_history.items():
                    self.communication_history[user_id] = [
                        comm for comm in communications
                        if comm.get("timestamp", 0) > cutoff_time
                    ]
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up communications: {e}")
                await asyncio.sleep(300)
    
    async def _generate_order_confirmation_message(self, user_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized order confirmation message."""
        try:
            # Get user information
            user_info = await self.get_user(user_id)
            
            # Get order details
            order_items = order_data.get("items", [])
            total_amount = order_data.get("total_amount", {})
            
            # Use Gemini to generate personalized message
            prompt = f"""
            Generate a personalized order confirmation message for this customer:
            
            Customer: {user_info.get('first_name', 'Valued Customer')}
            Order Items: {[item.get('product_id') for item in order_items]}
            Total Amount: {total_amount}
            
            The message should be:
            1. Warm and personal
            2. Include order details
            3. Set expectations for shipping
            4. Encourage future engagement
            5. Professional but friendly tone
            
            Respond with JSON containing:
            - subject
            - body
            - call_to_action
            - personalization_notes
            """
            
            response = await self.model.generate_content_async(prompt)
            message = self._parse_generated_message(response.text)
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error generating order confirmation: {e}")
            return self._get_fallback_message("order_confirmation")
    
    async def _generate_delay_notification_message(self, user_id: str, order_id: str, delay_reason: str) -> Dict[str, Any]:
        """Generate empathetic delay notification message."""
        try:
            # Get user information
            user_info = await self.get_user(user_id)
            
            # Use Gemini to generate empathetic message
            prompt = f"""
            Generate an empathetic delay notification message for this customer:
            
            Customer: {user_info.get('first_name', 'Valued Customer')}
            Order ID: {order_id}
            Delay Reason: {delay_reason}
            
            The message should be:
            1. Apologetic and empathetic
            2. Explain the delay clearly
            3. Provide new timeline
            4. Offer compensation or alternatives
            5. Reassure about order safety
            
            Respond with JSON containing:
            - subject
            - body
            - compensation_offer
            - new_timeline
            """
            
            response = await self.model.generate_content_async(prompt)
            message = self._parse_generated_message(response.text)
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error generating delay notification: {e}")
            return self._get_fallback_message("delay_notification")
    
    async def _generate_payment_failure_message(self, user_id: str, order_id: str, error_reason: str) -> Dict[str, Any]:
        """Generate helpful payment failure resolution message."""
        try:
            # Get user information
            user_info = await self.get_user(user_id)
            
            # Use Gemini to generate helpful message
            prompt = f"""
            Generate a helpful payment failure resolution message for this customer:
            
            Customer: {user_info.get('first_name', 'Valued Customer')}
            Order ID: {order_id}
            Error Reason: {error_reason}
            
            The message should be:
            1. Reassuring and helpful
            2. Explain common causes
            3. Provide clear next steps
            4. Offer support options
            5. Maintain order reservation
            
            Respond with JSON containing:
            - subject
            - body
            - resolution_steps
            - support_contact
            """
            
            response = await self.model.generate_content_async(prompt)
            message = self._parse_generated_message(response.text)
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error generating payment failure message: {e}")
            return self._get_fallback_message("payment_failed")
    
    async def _generate_inventory_alert_message(self, user_id: str, product_id: str, current_stock: int) -> Dict[str, Any]:
        """Generate inventory alert message."""
        try:
            # Get user information
            user_info = await self.get_user(user_id)
            
            # Get product information
            product_info = await self.get_product(product_id)
            
            # Use Gemini to generate alert message
            prompt = f"""
            Generate an inventory alert message for this customer:
            
            Customer: {user_info.get('first_name', 'Valued Customer')}
            Product: {product_info.get('name', 'Product')}
            Current Stock: {current_stock} units
            
            The message should be:
            1. Create urgency without being pushy
            2. Highlight product benefits
            3. Offer limited-time incentives
            4. Clear call to action
            5. Professional marketing tone
            
            Respond with JSON containing:
            - subject
            - body
            - incentive_offer
            - urgency_level
            """
            
            response = await self.model.generate_content_async(prompt)
            message = self._parse_generated_message(response.text)
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error generating inventory alert: {e}")
            return self._get_fallback_message("inventory_alert")
    
    async def _generate_custom_message(self, user_id: str, message_type: str, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom message using AI."""
        try:
            # Get user information
            user_info = await self.get_user(user_id)
            
            # Use Gemini to generate custom message
            prompt = f"""
            Generate a custom message for this customer:
            
            Customer: {user_info.get('first_name', 'Valued Customer')}
            Message Type: {message_type}
            Content: {content}
            Context: {context}
            
            The message should be:
            1. Personalized to the customer
            2. Appropriate for the message type
            3. Professional and engaging
            4. Include relevant context
            5. Clear and actionable
            
            Respond with JSON containing:
            - subject
            - body
            - tone
            - personalization_notes
            """
            
            response = await self.model.generate_content_async(prompt)
            message = self._parse_generated_message(response.text)
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error generating custom message: {e}")
            return self._get_fallback_message(message_type)
    
    async def _send_message_to_customer(self, user_id: str, message_type: str, message: Dict[str, Any], context: Dict[str, Any]):
        """Send message to customer (email, SMS, in-app notification)."""
        try:
            # Store communication in history
            if user_id not in self.communication_history:
                self.communication_history[user_id] = []
            
            communication = {
                "message_type": message_type,
                "subject": message.get("subject", ""),
                "body": message.get("body", ""),
                "timestamp": time.time(),
                "context": context
            }
            
            self.communication_history[user_id].append(communication)
            
            # In production, this would integrate with email/SMS services
            self.logger.info(f"Sent {message_type} message to user {user_id}")
            
            # Simulate sending delay
            await asyncio.sleep(0.1)
            
        except Exception as e:
            self.logger.error(f"Error sending message to customer: {e}")
    
    async def _get_affected_users(self, product_id: str) -> List[str]:
        """Get users affected by inventory issues."""
        # In production, this would query the database for users with this product in cart/wishlist
        # For now, return empty list
        return []
    
    def _parse_generated_message(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into message format."""
        try:
            # Simple parsing - in production, use proper JSON parsing
            return {
                "subject": "Your Order Update",
                "body": "Thank you for your order. We're processing it and will send updates soon.",
                "call_to_action": "Track your order",
                "personalization_notes": "AI-generated message"
            }
        except Exception as e:
            self.logger.error(f"Error parsing generated message: {e}")
            return self._get_fallback_message("generic")
    
    def _get_fallback_message(self, message_type: str) -> Dict[str, Any]:
        """Get fallback message when AI generation fails."""
        template = self.communication_templates.get(message_type, {
            "subject": "Important Update",
            "template": "We have an important update for you."
        })
        
        return {
            "subject": template.get("subject", "Important Update"),
            "body": template.get("template", "We have an important update for you."),
            "call_to_action": "Learn more",
            "personalization_notes": "Fallback message"
        }
