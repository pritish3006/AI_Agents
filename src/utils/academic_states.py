from typing import TypeVar, Dict, Any, List, Optional
from typing_extensions import TypedDict, Annotated
from datetime import datetime
from .reducers import dict_reducer, list_append_reducer, list_unique_reducer
from src.agents.base_agent import AgentState
from src.agents.models.coordination import ValidationResult

class StudentProfileRequired(TypedDict):
    """Required student profile fields."""
    id: str
    name: str
    type: str  # type of user (e.g., "student", "teacher", etc.)

class StudentProfile(StudentProfileRequired, total=False):
    """Student profile information with optional fields."""
    level: Optional[str]
    learning_goals: Annotated[List[str], list_unique_reducer]  # user's learning goals
    courses: Annotated[List[str], list_unique_reducer]
    topics: Annotated[List[str], list_unique_reducer]
    preferences: Annotated[Dict[str, Any], dict_reducer]
    history: Annotated[List[Dict[str, Any]], list_append_reducer]

class CalendarEvent(TypedDict):
    """Academic calendar event."""
    id: str
    title: str
    type: str  # class, assignment, exam, etc.
    start_time: datetime
    end_time: datetime
    description: str
    metadata: Dict[str, Any]

class AcademicTask(TypedDict):
    """Academic task or assignment."""
    id: str
    title: str
    description: str
    due_date: Optional[datetime]
    status: str
    priority: int
    attachments: List[str]
    metadata: Dict[str, Any]

class ProgressMetric(TypedDict):
    """flexible progress tracking for academic tasks/courses"""
    metric_type: str # e.g. grade, completion_rate, practice_time, etc.
    value: float # actual value of the metric
    timestamp: datetime # when the metric was last updated
    metadata: Dict[str, Any] # additional context about the metric

class FeedbackItem(TypedDict):
    """Feedback item for a specific task/course"""
    feedback_type: str # e.g. suggestion, encouragement, correction, etc.
    content: str # the content of the feedback
    context: Dict[str, Any] # additional context about the feedback
    timestamp: datetime # when the feedback was given

class InteractionResult(TypedDict):
    """Result of agent interaction with the user"""
    Interaction_type: str # e.g. question, exercise, quiz, assessment, project, etc.
    content: Any # the content of the interaction
    timestamp: datetime # when the result was given
    metadata: Dict[str, Any] # additional context about the interaction

class AcademicState(AgentState):
    """
    Master state container for the academic assistance system.
    Inherits from base AgentState for consistent state management.
    """
    model_config = {"arbitrary_types_allowed": True}
    
    # Student information
    profile: Annotated[StudentProfile, dict_reducer]
    
    # Calendar management
    calendar: Annotated[Dict[str, CalendarEvent], dict_reducer]
    upcoming_events: Annotated[List[str], list_append_reducer]
    
    # Task tracking
    tasks: Annotated[Dict[str, AcademicTask], dict_reducer]
    active_tasks: Annotated[List[str], list_unique_reducer]
    completed_tasks: Annotated[List[str], list_append_reducer]
    
    # Academic progress
    progress: Annotated[Dict[str, List[ProgressMetric]], dict_reducer] # the key here can be the course/topic/skill/etc.
    
    # Support and assistance
    learning_resources: Annotated[Dict[str, List[str]], dict_reducer]
    study_plans: Annotated[Dict[str, Any], dict_reducer]
    
    # Results and feedback
    results: Annotated[Dict[str, Any], dict_reducer]
    feedback: Annotated[List[Dict[str, Any]], list_append_reducer]
    
    # System state
    validation: Annotated[ValidationResult, dict_reducer]
    notifications: Annotated[List[Dict[str, Any]], list_append_reducer]

    def merge(self, other: 'AcademicState') -> 'AcademicState':
        """
        Merge two academic states using the defined reducers.
        Inherits base merge behavior and adds academic-specific merging.
        """
        # First merge base state
        base_merged = super().merge(other)
        
        # Then merge academic-specific state
        merged_state = AcademicState(
            # Base state components from parent
            **base_merged,
            
            # Academic components with appropriate reducers
            profile=dict_reducer(self.profile, other.profile),
            calendar=dict_reducer(self.calendar, other.calendar),
            upcoming_events=list_append_reducer(self.upcoming_events, other.upcoming_events),
            tasks=dict_reducer(self.tasks, other.tasks),
            active_tasks=list_unique_reducer(self.active_tasks, other.active_tasks),
            completed_tasks=list_append_reducer(self.completed_tasks, other.completed_tasks),
            progress=dict_reducer(self.progress, other.progress),
            learning_resources=dict_reducer(self.learning_resources, other.learning_resources),
            study_plans=dict_reducer(self.study_plans, other.study_plans),
            results=dict_reducer(self.results, other.results),
            feedback=list_append_reducer(self.feedback, other.feedback),
            validation=dict_reducer(self.validation.model_dump(), other.validation.model_dump()),
            notifications=list_append_reducer(self.notifications, other.notifications)
        )
        
        return merged_state 