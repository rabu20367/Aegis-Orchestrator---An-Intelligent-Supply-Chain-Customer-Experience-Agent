"""Configuration settings for Aegis Orchestrator."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Google AI Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-pro", env="GEMINI_MODEL")
    
    # Online Boutique Configuration
    boutique_base_url: str = Field(
        default="http://frontend:80", 
        env="BOUTIQUE_BASE_URL"
    )
    boutique_api_url: str = Field(
        default="http://frontend:80/api", 
        env="BOUTIQUE_API_URL"
    )
    
    # MCP Server Configuration
    mcp_server_host: str = Field(default="0.0.0.0", env="MCP_SERVER_HOST")
    mcp_server_port: int = Field(default=8001, env="MCP_SERVER_PORT")
    
    # Agent Configuration
    orchestrator_agent_name: str = Field(default="orchestrator", env="ORCHESTRATOR_AGENT_NAME")
    personalization_agent_name: str = Field(default="personalization", env="PERSONALIZATION_AGENT_NAME")
    inventory_agent_name: str = Field(default="inventory", env="INVENTORY_AGENT_NAME")
    customer_comms_agent_name: str = Field(default="customer_comms", env="CUSTOMER_COMMS_AGENT_NAME")
    anomaly_resolver_agent_name: str = Field(default="anomaly_resolver", env="ANOMALY_RESOLVER_AGENT_NAME")
    
    # A2A Communication
    a2a_broker_url: str = Field(default="redis://redis:6379", env="A2A_BROKER_URL")
    a2a_topic_prefix: str = Field(default="aegis", env="A2A_TOPIC_PREFIX")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./aegis.db", env="DATABASE_URL")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://redis:6379", env="REDIS_URL")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
