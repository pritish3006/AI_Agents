from typing import Dict, Type, Optional
from .base_agent import BaseAgent

class AgentRegistry:
    """
    Registry for managing agent types and their implementations.
    Implements the Singleton pattern to ensure only one registry exists.
    """
    _instance = None
    _agents: Dict[str, Type[BaseAgent]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
        return cls._instance
    
    def register(self, agent_type: str):
        """
        Decorator to register an agent implementation.
        
        Usage:
            @agent_registry.register("learning_path")
            class LearningPathAgent(BaseAgent):
                pass
        """
        def wrapper(agent_class: Type[BaseAgent]) -> Type[BaseAgent]:
            if not issubclass(agent_class, BaseAgent):
                raise ValueError(f"Agent class {agent_class.__name__} must inherit from BaseAgent")
            
            self._agents[agent_type] = agent_class
            return agent_class
        return wrapper
    
    def get_agent_class(self, agent_type: str) -> Optional[Type[BaseAgent]]:
        """Get the agent class for a given agent type."""
        return self._agents.get(agent_type)
    
    def list_agents(self) -> Dict[str, Type[BaseAgent]]:
        """List all registered agent types and their implementations."""
        return self._agents.copy()
    
    def unregister(self, agent_type: str) -> None:
        """Unregister an agent type."""
        self._agents.pop(agent_type, None)

# Global registry instance
agent_registry = AgentRegistry() 