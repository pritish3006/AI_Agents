from typing import Dict, Any, List, Tuple, TypeVar, Optional
from abc import ABC, abstractmethod
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from langchain.schema import BaseMessage, HumanMessage, AIMessage

# Define a generic type for state
StateType = TypeVar("StateType", bound=BaseModel)

class AgentState(BaseModel):
    """Base state model for agents."""
    # Conversation history using LangChain message types
    messages: List[BaseMessage] = Field(default_factory=list)
    # Current step in the workflow
    next_step: str = Field(default="start")
    # Additional context and metadata
    context: Dict[str, Any] = Field(default_factory=dict)
    # Status and error handling
    status: str = Field(default="running")
    error: Optional[str] = Field(default=None)

    def merge(self, other: 'AgentState') -> Dict[str, Any]:
        """
        Merge base state fields.
        
        Args:
            other (AgentState): Another state to merge with
            
        Returns:
            Dict[str, Any]: Merged base state fields
        """
        return {
            "messages": self.messages + other.messages,
            "next_step": other.next_step,
            "context": {**self.context, **other.context},
            "status": other.status,
            "error": other.error if other.error else self.error
        }

class BaseAgent(ABC):
    """Base agent class for all specialized agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.state_graph = self._create_state_graph()
    
    def add_message_to_state(self, state: AgentState, message: str, role: str = "human") -> AgentState:
        """Add a message to the state's message history."""
        if role == "human":
            state.messages.append(HumanMessage(content=message))
        else:
            state.messages.append(AIMessage(content=message))
        return state
    
    @abstractmethod
    def _create_state_graph(self) -> StateGraph:
        """Create the state graph for this agent using LangGraph."""
        pass
    
    @abstractmethod
    async def process(self, state: AgentState) -> Tuple[AgentState, str]:
        """
        Process the current state and return updated state and next step.
        Returns:
            Tuple[AgentState, str]: Updated state and the next step in the workflow
        """
        pass
    
    def _create_basic_workflow(self) -> StateGraph:
        """Create a basic workflow graph."""
        # Initialize the graph with our state type
        workflow = StateGraph(AgentState)
        
        # Define the process node
        async def process_node(state: AgentState) -> Tuple[AgentState, str]:
            try:
                return await self.process(state)
            except Exception as e:
                state.status = "error"
                state.error = str(e)
                return state, END
        
        # Add nodes
        workflow.add_node("start", process_node)
        
        # Add conditional edges based on next_step
        workflow.add_conditional_edges(
            "start",
            lambda x: x.next_step if x.next_step != "start" else END
        )
        
        # Compile the graph
        workflow.compile()
        
        return workflow
    
    async def execute(self, initial_input: str = None, context: Dict[str, Any] = None) -> AgentState:
        """Execute the agent's workflow."""
        # Initialize state
        state = AgentState(
            messages=[],
            next_step="start",
            context=context or {},
            status="running"
        )
        
        # Add initial input if provided
        if initial_input:
            state = self.add_message_to_state(state, initial_input)
        
        # Execute the workflow
        try:
            result = await self.state_graph.arun(state)
            return result
        except Exception as e:
            state.status = "error"
            state.error = str(e)
            return state