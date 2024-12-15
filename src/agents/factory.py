from typing import Dict, Any, Optional
from .registry import AgentRegistry
from .base_agent import BaseAgent
from src.config import AppConfig

class AgentFactory:
    """
    Factory for creating agent instances.
    Handles agent initialization, configuration, and dependency injection.
    """
    
    def __init__(
        self,
        registry: AgentRegistry,
        config: AppConfig,
        dependencies: Optional[Dict[str, Any]] = None
    ):
        self.registry = registry
        self.config = config
        self.dependencies = dependencies or {}
        
    def create(
        self,
        agent_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> BaseAgent:
        """
        Create an agent instance of the specified type.
        
        Args:
            agent_type: Type of agent to create
            context: Additional context for agent initialization
            
        Returns:
            Initialized agent instance
            
        Raises:
            ValueError: If agent type is not registered
        """
        # Get agent class from registry
        agent_class = self.registry.get_agent_class(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Create agent instance with name
        agent_name = f"{agent_type}_{id(context)}"
        agent = agent_class(name=agent_name)
        
        # Inject dependencies if agent needs them
        if hasattr(agent, 'set_dependencies'):
            agent.set_dependencies(self.dependencies)
        
        # Set any additional context
        if context and hasattr(agent, 'set_context'):
            agent.set_context(context)
        
        return agent
    
    def get_available_agents(self) -> Dict[str, str]:
        """Get list of available agent types and their descriptions."""
        agents = self.registry.list_agents()
        return {
            agent_type: agent_class.__doc__ or "No description available"
            for agent_type, agent_class in agents.items()
        } 