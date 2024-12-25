from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field
from enum import Enum

class ComplexityLevel(str, Enum):
    """Complexity levels for request analysis."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RequestType(str, Enum):
    """Types of requests that can be handled."""
    QUERY = "query"
    TASK = "task"
    ANALYSIS = "analysis"
    CREATION = "creation"
    MODIFICATION = "modification"
    ORCHESTRATION = "orchestration"

class TimeConstraints(BaseModel):
    """Time constraints for execution."""
    max_duration: Optional[float] = None
    deadline: Optional[str] = None
    priority_level: int = Field(default=1, ge=1, le=5)

class ProfileData(BaseModel):
    """User profile and context data."""
    user_id: str
    preferences: Dict[str, Any] = Field(default_factory=dict)
    history: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)

class ContextAnalysis(BaseModel):
    """Comprehensive context analysis results."""
    profile_data: ProfileData
    request_type: RequestType
    complexity_level: ComplexityLevel
    time_constraints: Optional[TimeConstraints] = None
    required_capabilities: List[str] = Field(default_factory=list)
    additional_context: Dict[str, Any] = Field(default_factory=dict)

class ValidationResult(BaseModel):
    """Results of validation checks."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

class AgentGroupConfig(BaseModel):
    """Configuration for a group of agents."""
    agents: List[str]
    dependencies: Set[str] = Field(default_factory=set)
    fallback_group: Optional[str] = None
    required_capabilities: List[str] = Field(default_factory=list)
    max_retries: int = Field(default=3, ge=0)
    timeout: Optional[float] = None

class CoordinationState(BaseModel):
    """State tracking for coordination."""
    active_groups: Set[str] = Field(default_factory=set)
    completed_groups: Set[str] = Field(default_factory=set)
    failed_groups: Set[str] = Field(default_factory=set)
    current_phase: int = Field(default=0)
    errors: Dict[str, List[str]] = Field(default_factory=dict)
    results: Dict[str, Any] = Field(default_factory=dict)

class CoordinationPlan(BaseModel):
    """Complete coordination plan with LLM reasoning."""
    groups: Dict[str, AgentGroupConfig]
    execution_order: List[Set[str]]
    fallback_chain: List[str]
    context_analysis: ContextAnalysis
    reasoning: str
    validation: ValidationResult
    state: CoordinationState = Field(default_factory=CoordinationState)

class ReActStep(BaseModel):
    """Single step in ReACT framework."""
    thought: str
    action: str
    action_input: Dict[str, Any]
    observation: Optional[str] = None

class ReActTrace(BaseModel):
    """Complete trace of ReACT reasoning."""
    steps: List[ReActStep] = Field(default_factory=list)
    final_answer: Optional[str] = None 