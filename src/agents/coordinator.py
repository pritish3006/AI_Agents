from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from enum import Enum
from .base_agent import AgentState

class ExecutionPriority(str, Enum):
    """Priority levels for agent execution."""
    HIGH = "high"       # Critical path agents
    MEDIUM = "medium"   # Important but not critical
    LOW = "low"        # Optional enhancements
    FALLBACK = "fallback"  # Fallback agents

class ExecutionStatus(str, Enum):
    """Status of agent execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    FALLBACK = "fallback"

@dataclass
class AgentGroup:
    """Group of agents that can be executed concurrently."""
    agents: Set[str]  # Agent types in this group
    priority: ExecutionPriority
    dependencies: Set[str] = None  # Agent groups that must complete first
    fallback_group: Optional[str] = None  # Fallback group if this fails

@dataclass
class CoordinationPlan:
    """Complete plan for agent coordination."""
    groups: Dict[str, AgentGroup]  # Group ID -> Group
    execution_order: List[Set[str]]  # Sets of group IDs that can run concurrently
    fallback_chain: List[str]  # Chain of fallback groups to try
    
class CoordinationAnalyzer:
    """Analyzes coordination requirements and creates execution plans."""
    
    @staticmethod
    def extract_coordination_from_state(state: AgentState) -> Optional[CoordinationPlan]:
        """Extract coordination plan from coordinator agent state."""
        try:
            if not state.messages:
                return None
                
            # Get the latest message
            latest_message = state.messages[-1].content
            
            # TODO: Implement actual coordination analysis
            # For now, return a basic plan
            return CoordinationAnalyzer.create_default_plan()
            
        except Exception as e:
            # Log error and return default plan
            print(f"Error extracting coordination plan: {e}")
            return CoordinationAnalyzer.create_fallback_plan()
    
    @staticmethod
    def create_default_plan() -> CoordinationPlan:
        """Create a default coordination plan."""
        groups = {
            "primary": AgentGroup(
                agents={"learning_path"},
                priority=ExecutionPriority.HIGH,
                fallback_group="fallback"
            ),
            "secondary": AgentGroup(
                agents={"content_processor"},
                priority=ExecutionPriority.MEDIUM,
                dependencies={"primary"}
            ),
            "fallback": AgentGroup(
                agents={"basic_agent"},
                priority=ExecutionPriority.FALLBACK
            )
        }
        
        execution_order = [{"primary"}, {"secondary"}]
        fallback_chain = ["fallback"]
        
        return CoordinationPlan(
            groups=groups,
            execution_order=execution_order,
            fallback_chain=fallback_chain
        )
    
    @staticmethod
    def create_fallback_plan() -> CoordinationPlan:
        """Create an emergency fallback plan."""
        groups = {
            "emergency": AgentGroup(
                agents={"basic_agent"},
                priority=ExecutionPriority.FALLBACK
            )
        }
        
        return CoordinationPlan(
            groups=groups,
            execution_order=[{"emergency"}],
            fallback_chain=[]
        )
    
    @staticmethod
    def validate_plan(plan: CoordinationPlan) -> bool:
        """Validate a coordination plan for consistency."""
        try:
            # Check all groups exist
            all_groups = set(plan.groups.keys())
            
            # Check execution order references valid groups
            for group_set in plan.execution_order:
                if not group_set.issubset(all_groups):
                    return False
            
            # Check dependencies exist
            for group in plan.groups.values():
                if group.dependencies and not group.dependencies.issubset(all_groups):
                    return False
                if group.fallback_group and group.fallback_group not in all_groups:
                    return False
            
            # Check fallback chain references valid groups
            if not set(plan.fallback_chain).issubset(all_groups):
                return False
            
            return True
            
        except Exception:
            return False 