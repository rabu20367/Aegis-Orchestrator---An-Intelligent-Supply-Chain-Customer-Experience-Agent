"""Personalization Agent - AI-powered recommendation engine."""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
import google.generativeai as genai
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from agents.base_agent import BaseAgent, AgentMessage, AgentResponse
from config.settings import settings


class PersonalizationAgent(BaseAgent):
    """AI-powered personalization agent for recommendations and dynamic pricing."""
    
    def __init__(self):
        super().__init__(
            agent_id="personalization-agent",
            agent_name="personalization"
        )
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        
        # User profiles and preferences
        self.user_profiles = {}
        self.product_features = {}
        self.recommendation_cache = {}
        
        # ML components
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.product_vectors = None
        
    async def initialize(self):
        """Initialize the personalization agent."""
        self.logger.info("Initializing Personalization Agent")
        
        # Load product catalog and build feature vectors
        await self._build_product_features()
        
        # Start background tasks
        asyncio.create_task(self._update_user_profiles())
        asyncio.create_task(self._refresh_recommendations())
        
        self.logger.info("Personalization Agent initialized")
    
    async def cleanup(self):
        """Cleanup personalization resources."""
        self.logger.info("Cleaning up Personalization Agent")
    
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
        """Handle personalization events."""
        event_type = event_data.get("event_type")
        
        if event_type == "user_browsing":
            return await self._handle_user_browsing(event_data)
        elif event_type == "cart_updated":
            return await self._handle_cart_updated(event_data)
        elif event_type == "order_created":
            return await self._handle_order_created(event_data)
        else:
            return AgentResponse(success=False, error=f"Unknown event type: {event_type}")
    
    async def _handle_request(self, request_data: Dict[str, Any]) -> AgentResponse:
        """Handle personalization requests."""
        request_type = request_data.get("request_type")
        
        if request_type == "get_recommendations":
            return await self._get_recommendations(request_data)
        elif request_type == "get_dynamic_pricing":
            return await self._get_dynamic_pricing(request_data)
        elif request_type == "get_bundle_suggestions":
            return await self._get_bundle_suggestions(request_data)
        else:
            return AgentResponse(success=False, error=f"Unknown request type: {request_type}")
    
    async def _handle_user_browsing(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user browsing events to update preferences."""
        user_id = event_data.get("user_id")
        page = event_data.get("page")
        products_viewed = event_data.get("products_viewed", [])
        
        self.logger.info(f"Updating preferences for user {user_id} browsing {page}")
        
        # Update user profile with browsing behavior
        await self._update_user_profile(user_id, {
            "browsing_history": products_viewed,
            "last_page": page,
            "timestamp": time.time()
        })
        
        # Generate immediate recommendations
        recommendations = await self._generate_recommendations(user_id, products_viewed)
        
        return {
            "status": "preferences_updated",
            "user_id": user_id,
            "recommendations": recommendations
        }
    
    async def _handle_cart_updated(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cart updates for upsell opportunities."""
        user_id = event_data.get("user_id")
        cart_data = event_data.get("cart_data")
        
        self.logger.info(f"Analyzing cart for upsell opportunities for user {user_id}")
        
        # Get cart items
        cart_items = cart_data.get("items", [])
        
        # Generate upsell recommendations
        upsell_recommendations = await self._generate_upsell_recommendations(user_id, cart_items)
        
        # Generate bundle suggestions
        bundle_suggestions = await self._generate_bundle_suggestions(user_id, cart_items)
        
        return {
            "status": "cart_analyzed",
            "user_id": user_id,
            "upsell_recommendations": upsell_recommendations,
            "bundle_suggestions": bundle_suggestions
        }
    
    async def _handle_order_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle order creation to update user preferences."""
        user_id = event_data.get("user_id")
        order_data = event_data.get("order_data")
        
        self.logger.info(f"Updating preferences based on order for user {user_id}")
        
        # Extract purchase preferences
        order_items = order_data.get("items", [])
        purchased_products = [item.get("product_id") for item in order_items]
        
        # Update user profile with purchase behavior
        await self._update_user_profile(user_id, {
            "purchase_history": purchased_products,
            "last_purchase": time.time()
        })
        
        return {
            "status": "preferences_updated",
            "user_id": user_id
        }
    
    async def _get_recommendations(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get personalized recommendations for a user."""
        user_id = request_data.get("user_id")
        cart_data = request_data.get("cart_data", {})
        limit = request_data.get("limit", 5)
        
        # Get user profile
        user_profile = await self._get_user_profile(user_id)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(user_id, cart_data.get("items", []))
        
        return {
            "status": "recommendations_generated",
            "user_id": user_id,
            "recommendations": recommendations[:limit]
        }
    
    async def _get_dynamic_pricing(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get dynamic pricing suggestions."""
        user_id = request_data.get("user_id")
        product_id = request_data.get("product_id")
        base_price = request_data.get("base_price", 0)
        
        # Get user profile for pricing strategy
        user_profile = await self._get_user_profile(user_id)
        
        # Use Gemini to determine pricing strategy
        pricing_strategy = await self._determine_pricing_strategy(user_profile, product_id, base_price)
        
        return {
            "status": "pricing_calculated",
            "user_id": user_id,
            "product_id": product_id,
            "original_price": base_price,
            "suggested_price": pricing_strategy.get("price", base_price),
            "discount_percentage": pricing_strategy.get("discount_percentage", 0),
            "reasoning": pricing_strategy.get("reasoning", "")
        }
    
    async def _get_bundle_suggestions(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get bundle suggestions for cart items."""
        user_id = request_data.get("user_id")
        cart_items = request_data.get("cart_items", [])
        
        # Generate bundle suggestions
        bundles = await self._generate_bundle_suggestions(user_id, cart_items)
        
        return {
            "status": "bundles_generated",
            "user_id": user_id,
            "bundles": bundles
        }
    
    async def _build_product_features(self):
        """Build product feature vectors for similarity calculations."""
        try:
            # Get all products
            products = await self.get_products()
            
            # Extract product features
            product_descriptions = []
            product_ids = []
            
            for product in products:
                product_ids.append(product.get("id"))
                description = f"{product.get('name', '')} {product.get('description', '')} {' '.join(product.get('categories', []))}"
                product_descriptions.append(description)
            
            # Build TF-IDF vectors
            if product_descriptions:
                self.product_vectors = self.vectorizer.fit_transform(product_descriptions)
                self.product_features = dict(zip(product_ids, product_descriptions))
                
                self.logger.info(f"Built feature vectors for {len(product_ids)} products")
            
        except Exception as e:
            self.logger.error(f"Error building product features: {e}")
    
    async def _update_user_profile(self, user_id: str, data: Dict[str, Any]):
        """Update user profile with new data."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "browsing_history": [],
                "purchase_history": [],
                "preferences": {},
                "created_at": time.time()
            }
        
        # Update profile
        for key, value in data.items():
            if key in ["browsing_history", "purchase_history"]:
                # Append to lists
                if key not in self.user_profiles[user_id]:
                    self.user_profiles[user_id][key] = []
                self.user_profiles[user_id][key].extend(value if isinstance(value, list) else [value])
            else:
                self.user_profiles[user_id][key] = value
        
        # Update timestamp
        self.user_profiles[user_id]["last_updated"] = time.time()
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile, creating if doesn't exist."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "browsing_history": [],
                "purchase_history": [],
                "preferences": {},
                "created_at": time.time()
            }
        
        return self.user_profiles[user_id]
    
    async def _generate_recommendations(self, user_id: str, current_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations using AI and ML."""
        try:
            # Get user profile
            user_profile = await self._get_user_profile(user_id)
            
            # Get all products
            products = await self.get_products()
            
            # Use Gemini to generate recommendations
            prompt = f"""
            As a personalization AI, recommend products for this user:
            
            User Profile:
            - Browsing History: {user_profile.get('browsing_history', [])}
            - Purchase History: {user_profile.get('purchase_history', [])}
            - Current Cart Items: {[item.get('product_id') for item in current_items]}
            
            Available Products: {[p.get('name') for p in products[:10]]}
            
            Please recommend 5 products that would be most relevant to this user.
            Consider:
            1. Similar products to their browsing/purchase history
            2. Complementary products to their current cart
            3. Popular products in their preferred categories
            4. Products that match their price range preferences
            
            Respond with a JSON array of product recommendations with:
            - product_id
            - reason
            - confidence_score (0-1)
            - category
            """
            
            response = await self.model.generate_content_async(prompt)
            recommendations = self._parse_recommendations(response.text, products)
            
            # Cache recommendations
            self.recommendation_cache[user_id] = {
                "recommendations": recommendations,
                "timestamp": time.time()
            }
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def _generate_upsell_recommendations(self, user_id: str, cart_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate upsell recommendations for cart items."""
        try:
            # Get user profile
            user_profile = await self._get_user_profile(user_id)
            
            # Use Gemini to generate upsell recommendations
            prompt = f"""
            As a personalization AI, suggest upsell products for this cart:
            
            Cart Items: {[item.get('product_id') for item in cart_items]}
            User History: {user_profile.get('purchase_history', [])}
            
            Suggest 3-5 products that would be good upsells:
            1. Higher-end versions of items in cart
            2. Complementary accessories
            3. Popular add-ons
            
            Respond with JSON array of upsell recommendations.
            """
            
            response = await self.model.generate_content_async(prompt)
            upsells = self._parse_recommendations(response.text, await self.get_products())
            
            return upsells
            
        except Exception as e:
            self.logger.error(f"Error generating upsell recommendations: {e}")
            return []
    
    async def _generate_bundle_suggestions(self, user_id: str, cart_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate bundle suggestions for cart items."""
        try:
            # Use Gemini to generate bundle suggestions
            prompt = f"""
            As a personalization AI, suggest product bundles for this cart:
            
            Cart Items: {[item.get('product_id') for item in cart_items]}
            
            Suggest 2-3 bundle combinations that would:
            1. Complete the look/style
            2. Offer good value with discount
            3. Include popular complementary items
            
            Respond with JSON array of bundle suggestions with:
            - bundle_name
            - products (array of product_ids)
            - discount_percentage
            - total_savings
            - reasoning
            """
            
            response = await self.model.generate_content_async(prompt)
            bundles = self._parse_bundle_suggestions(response.text)
            
            return bundles
            
        except Exception as e:
            self.logger.error(f"Error generating bundle suggestions: {e}")
            return []
    
    async def _determine_pricing_strategy(self, user_profile: Dict[str, Any], product_id: str, base_price: float) -> Dict[str, Any]:
        """Determine dynamic pricing strategy using AI."""
        try:
            prompt = f"""
            As a pricing AI, determine the optimal price for this product:
            
            Product ID: {product_id}
            Base Price: ${base_price}
            User Profile: {user_profile}
            
            Consider:
            1. User's price sensitivity based on history
            2. Product popularity and demand
            3. Competitive positioning
            4. Inventory levels
            5. Seasonal factors
            
            Respond with JSON containing:
            - suggested_price
            - discount_percentage
            - reasoning
            - confidence_score
            """
            
            response = await self.model.generate_content_async(prompt)
            pricing = self._parse_pricing_strategy(response.text, base_price)
            
            return pricing
            
        except Exception as e:
            self.logger.error(f"Error determining pricing strategy: {e}")
            return {"price": base_price, "discount_percentage": 0, "reasoning": "Error in pricing calculation"}
    
    def _parse_recommendations(self, response_text: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse AI response into recommendation format."""
        try:
            # Simple parsing - in production, use proper JSON parsing
            recommendations = []
            
            # Create product lookup
            product_lookup = {p.get("id"): p for p in products}
            
            # For now, return some mock recommendations
            # In production, parse the actual AI response
            for product in products[:5]:
                recommendations.append({
                    "product_id": product.get("id"),
                    "name": product.get("name"),
                    "price": product.get("price_usd", {}).get("currencyCode", "USD"),
                    "reason": "AI-generated recommendation",
                    "confidence_score": 0.8,
                    "category": product.get("categories", [""])[0] if product.get("categories") else "General"
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error parsing recommendations: {e}")
            return []
    
    def _parse_bundle_suggestions(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse AI response into bundle format."""
        try:
            # Mock bundle suggestions
            return [
                {
                    "bundle_name": "Complete Look Bundle",
                    "products": ["product1", "product2"],
                    "discount_percentage": 15,
                    "total_savings": 25.50,
                    "reasoning": "Complete your style with these complementary items"
                }
            ]
        except Exception as e:
            self.logger.error(f"Error parsing bundle suggestions: {e}")
            return []
    
    def _parse_pricing_strategy(self, response_text: str, base_price: float) -> Dict[str, Any]:
        """Parse AI response into pricing strategy."""
        try:
            # Mock pricing strategy
            return {
                "price": base_price * 0.9,  # 10% discount
                "discount_percentage": 10,
                "reasoning": "First-time customer discount",
                "confidence_score": 0.8
            }
        except Exception as e:
            self.logger.error(f"Error parsing pricing strategy: {e}")
            return {"price": base_price, "discount_percentage": 0, "reasoning": "Error in parsing"}
    
    async def _update_user_profiles(self):
        """Background task to update user profiles."""
        while self.is_running:
            try:
                # Update user profiles based on recent activity
                # This would analyze user behavior and update preferences
                await asyncio.sleep(300)  # Update every 5 minutes
            except Exception as e:
                self.logger.error(f"Error updating user profiles: {e}")
                await asyncio.sleep(60)
    
    async def _refresh_recommendations(self):
        """Background task to refresh recommendation cache."""
        while self.is_running:
            try:
                # Refresh recommendations for active users
                # This would update the recommendation cache
                await asyncio.sleep(600)  # Refresh every 10 minutes
            except Exception as e:
                self.logger.error(f"Error refreshing recommendations: {e}")
                await asyncio.sleep(60)
