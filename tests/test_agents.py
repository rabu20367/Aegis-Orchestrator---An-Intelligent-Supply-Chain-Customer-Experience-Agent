"""Tests for AI Agents."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from agents.orchestrator.agent import OrchestratorAgent
from agents.personalization.agent import PersonalizationAgent
from agents.inventory.agent import InventoryAgent
from agents.customer_comms.agent import CustomerCommsAgent
from agents.anomaly_resolver.agent import AnomalyResolverAgent
from agents.base_agent import AgentMessage


class TestOrchestratorAgent:
    """Test cases for Orchestrator Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test orchestrator agent."""
        return OrchestratorAgent()
    
    @pytest.mark.asyncio
    async def test_handle_order_created_event(self, agent):
        """Test handling order created event."""
        event_data = {
            "event_type": "order_created",
            "order_id": "order-123",
            "user_id": "user-123",
            "order_data": {"items": [{"product_id": "prod-1", "quantity": 2}]}
        }
        
        with patch.object(agent, 'send_message') as mock_send:
            response = await agent._handle_order_created(event_data)
            
            assert response["status"] == "order_processing_initiated"
            assert response["order_id"] == "order-123"
            # Should send messages to inventory and customer comms agents
            assert mock_send.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_handle_cart_updated_event(self, agent):
        """Test handling cart updated event."""
        event_data = {
            "event_type": "cart_updated",
            "user_id": "user-123",
            "cart_data": {"items": [{"product_id": "prod-1", "quantity": 1}]}
        }
        
        with patch.object(agent, 'send_message') as mock_send:
            response = await agent._handle_cart_updated(event_data)
            
            assert response["status"] == "cart_analysis_initiated"
            assert response["user_id"] == "user-123"
            # Should send message to personalization agent
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_situation(self, agent):
        """Test situation analysis using Gemini."""
        request_data = {
            "situation_description": "High error rate detected",
            "context_data": {"error_rate": 0.1, "threshold": 0.05}
        }
        
        with patch.object(agent.model, 'generate_content_async') as mock_generate:
            mock_generate.return_value = MagicMock(text='{"analysis": "Test analysis"}')
            
            response = await agent._analyze_situation(request_data)
            
            assert response["status"] == "analysis_complete"
            assert "analysis" in response
            mock_generate.assert_called_once()


class TestPersonalizationAgent:
    """Test cases for Personalization Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test personalization agent."""
        return PersonalizationAgent()
    
    @pytest.mark.asyncio
    async def test_handle_user_browsing_event(self, agent):
        """Test handling user browsing event."""
        event_data = {
            "event_type": "user_browsing",
            "user_id": "user-123",
            "page": "product-page",
            "products_viewed": ["prod-1", "prod-2"]
        }
        
        with patch.object(agent, '_generate_recommendations') as mock_generate:
            mock_generate.return_value = [{"product_id": "prod-3", "reason": "Similar to viewed"}]
            
            response = await agent._handle_user_browsing(event_data)
            
            assert response["status"] == "preferences_updated"
            assert response["user_id"] == "user-123"
            assert "recommendations" in response
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, agent):
        """Test generating recommendations."""
        with patch.object(agent.model, 'generate_content_async') as mock_generate:
            mock_generate.return_value = MagicMock(text='[{"product_id": "prod-1", "reason": "AI recommendation"}]')
            
            recommendations = await agent._generate_recommendations("user-123", [])
            
            assert isinstance(recommendations, list)
            mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_recommendations_request(self, agent):
        """Test handling get recommendations request."""
        request_data = {
            "request_type": "get_recommendations",
            "user_id": "user-123",
            "cart_data": {"items": []},
            "limit": 5
        }
        
        with patch.object(agent, '_generate_recommendations') as mock_generate:
            mock_generate.return_value = [{"product_id": "prod-1"}]
            
            response = await agent._handle_request(request_data)
            
            assert response.success is True
            assert "recommendations" in response.data


class TestInventoryAgent:
    """Test cases for Inventory Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test inventory agent."""
        return InventoryAgent()
    
    @pytest.mark.asyncio
    async def test_handle_order_created_event(self, agent):
        """Test handling order created event."""
        event_data = {
            "event_type": "order_created",
            "order_id": "order-123",
            "order_data": {"items": [{"product_id": "prod-1", "quantity": 2}]}
        }
        
        # Mock inventory levels
        agent.inventory_levels = {"prod-1": {"total": 10}}
        agent.reorder_thresholds = {"prod-1": 5}
        
        with patch.object(agent, 'send_message') as mock_send:
            response = await agent._handle_order_created(event_data)
            
            assert response["status"] == "inventory_updated"
            assert response["order_id"] == "order-123"
            assert response["items_processed"] == 1
    
    @pytest.mark.asyncio
    async def test_handle_inventory_low_event(self, agent):
        """Test handling inventory low event."""
        event_data = {
            "event_type": "inventory_low",
            "product_id": "prod-1",
            "current_stock": 3
        }
        
        with patch.object(agent, 'send_message') as mock_send:
            with patch.object(agent, '_generate_reorder_suggestions') as mock_suggestions:
                mock_suggestions.return_value = [{"product_id": "prod-1", "reorder_quantity": 50}]
                
                response = await agent._handle_inventory_low(event_data)
                
                assert response["status"] == "low_inventory_handled"
                assert response["product_id"] == "prod-1"
                mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_demand_prediction(self, agent):
        """Test generating demand prediction."""
        with patch.object(agent.model, 'generate_content_async') as mock_generate:
            mock_generate.return_value = MagicMock(text='{"predicted_demand": [5, 6, 7]}')
            
            prediction = await agent._generate_demand_prediction("prod-1", 7)
            
            assert "predicted_demand" in prediction
            mock_generate.assert_called_once()


class TestCustomerCommsAgent:
    """Test cases for Customer Communications Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test customer comms agent."""
        return CustomerCommsAgent()
    
    @pytest.mark.asyncio
    async def test_handle_order_created_event(self, agent):
        """Test handling order created event."""
        event_data = {
            "event_type": "order_created",
            "order_id": "order-123",
            "user_id": "user-123",
            "order_data": {"items": [{"product_id": "prod-1", "quantity": 2}]}
        }
        
        with patch.object(agent, '_generate_order_confirmation_message') as mock_generate:
            with patch.object(agent, '_send_message_to_customer') as mock_send:
                mock_generate.return_value = {"subject": "Order Confirmation", "body": "Thank you!"}
                
                response = await agent._handle_order_created(event_data)
                
                assert response["status"] == "confirmation_sent"
                assert response["order_id"] == "order-123"
                mock_generate.assert_called_once()
                mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_order_confirmation_message(self, agent):
        """Test generating order confirmation message."""
        with patch.object(agent, 'get_user') as mock_get_user:
            with patch.object(agent.model, 'generate_content_async') as mock_generate:
                mock_get_user.return_value = {"first_name": "John"}
                mock_generate.return_value = MagicMock(text='{"subject": "Order Confirmation", "body": "Thank you John!"}')
                
                message = await agent._generate_order_confirmation_message("user-123", {"items": []})
                
                assert "subject" in message
                assert "body" in message
                mock_generate.assert_called_once()


class TestAnomalyResolverAgent:
    """Test cases for Anomaly Resolver Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test anomaly resolver agent."""
        return AnomalyResolverAgent()
    
    @pytest.mark.asyncio
    async def test_handle_payment_failure_event(self, agent):
        """Test handling payment failure event."""
        event_data = {
            "event_type": "payment_failed",
            "order_id": "order-123",
            "user_id": "user-123",
            "error_reason": "Insufficient funds"
        }
        
        with patch.object(agent, '_generate_payment_resolution_plan') as mock_generate:
            with patch.object(agent, '_execute_resolution_plan') as mock_execute:
                mock_generate.return_value = {"resolution_steps": []}
                mock_execute.return_value = {"status": "success"}
                
                response = await agent._handle_payment_failure(event_data)
                
                assert response["status"] == "payment_anomaly_handled"
                assert "anomaly_id" in response
                mock_generate.assert_called_once()
                mock_execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_payment_resolution_plan(self, agent):
        """Test generating payment resolution plan."""
        anomaly = {
            "order_id": "order-123",
            "user_id": "user-123",
            "error_reason": "Insufficient funds"
        }
        
        with patch.object(agent.model, 'generate_content_async') as mock_generate:
            mock_generate.return_value = MagicMock(text='{"resolution_steps": [{"type": "retry_payment"}]}')
            
            plan = await agent._generate_payment_resolution_plan(anomaly)
            
            assert "resolution_steps" in plan
            mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_detect_anomalies(self, agent):
        """Test detecting anomalies."""
        request_data = {"request_type": "detect_anomalies"}
        
        with patch.object(agent, '_collect_system_metrics') as mock_collect:
            with patch.object(agent, '_ai_anomaly_detection') as mock_detect:
                mock_collect.return_value = {"cpu_usage": 90}
                mock_detect.return_value = [{"anomaly_type": "performance_degradation"}]
                
                response = await agent._handle_request(request_data)
                
                assert response.success is True
                assert "anomalies" in response.data
                mock_collect.assert_called_once()
                mock_detect.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
