#!/usr/bin/env python3
"""
Main entry point for Aegis Orchestrator.

Author: Savnvancan
Email: sanworktech@gmail.com
"""

import asyncio
import logging
import sys
from typing import Optional

from agents.orchestrator.agent import OrchestratorAgent
from agents.personalization.agent import PersonalizationAgent
from agents.inventory.agent import InventoryAgent
from agents.customer_comms.agent import CustomerCommsAgent
from agents.anomaly_resolver.agent import AnomalyResolverAgent
from config.settings import settings


async def main():
    """Main function to start all agents."""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Aegis Orchestrator...")
    
    # Create agents
    agents = [
        OrchestratorAgent(),
        PersonalizationAgent(),
        InventoryAgent(),
        CustomerCommsAgent(),
        AnomalyResolverAgent()
    ]
    
    try:
        # Start all agents
        start_tasks = [agent.start() for agent in agents]
        await asyncio.gather(*start_tasks)
        
        logger.info("All agents started successfully")
        
        # Keep running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("Shutting down Aegis Orchestrator...")
        
        # Stop all agents
        stop_tasks = [agent.stop() for agent in agents]
        await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        logger.info("Aegis Orchestrator stopped")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
