import pytest
from datetime import datetime
from langchain.schema import HumanMessage
from src.utils.reducers import (
    dict_reducer,
    add,
    StudentProfile,
    CalendarEvent,
    AcademicTask,
    StudySession,
    LearningProgress,
    AcademicState,
    AgentState,
    InteractionState
)

def test_dict_reducer():
    """Test dictionary merging functionality."""
    dict1 = {
        "profile": {"name": "John", "courses": ["Math"]},
        "metrics": {"sessions": 1}
    }
    dict2 = {
        "profile": {"major": "CS", "courses": ["Physics"]},
        "results": {"test": "passed"}
    }
    
    result = dict_reducer(dict1, dict2)
    
    assert result["profile"]["name"] == "John"
    assert result["profile"]["major"] == "CS"
    assert result["metrics"]["sessions"] == 1
    assert result["results"]["test"] == "passed"

def test_list_add():
    """Test list combination functionality."""
    list1 = [HumanMessage(content="Hello")]
    list2 = [HumanMessage(content="World")]
    
    result = add(list1, list2)
    
    assert len(result) == 2
    assert result[0].content == "Hello"
    assert result[1].content == "World"

def test_student_profile():
    """Test student profile state creation."""
    profile: StudentProfile = {
        "student_id": "12345",
        "name": "John Doe",
        "academic_level": "undergraduate",
        "courses": ["CS101", "MATH201"],
        "preferences": {"study_time": "morning"},
        "learning_style": "visual",
        "strengths": ["programming", "problem-solving"]
    }
    
    assert isinstance(profile, dict)
    assert profile["student_id"] == "12345"
    assert len(profile["courses"]) == 2
    assert "learning_style" in profile

def test_calendar_event():
    """Test calendar event state."""
    event: CalendarEvent = {
        "event_id": "evt_1",
        "title": "CS101 Lecture",
        "event_type": "class",
        "start_time": datetime.now(),
        "end_time": datetime.now(),
        "course_id": "CS101",
        "location": "Room 101"
    }
    
    assert isinstance(event, dict)
    assert event["event_type"] == "class"
    assert isinstance(event["start_time"], datetime)

def test_academic_task():
    """Test academic task state."""
    task: AcademicTask = {
        "task_id": "task_1",
        "title": "Programming Assignment",
        "task_type": "assignment",
        "course_id": "CS101",
        "due_date": datetime.now(),
        "priority": 1,
        "status": "pending",
        "requirements": ["Python", "Git"],
        "progress": 0.5
    }
    
    assert isinstance(task, dict)
    assert task["task_type"] == "assignment"
    assert isinstance(task["progress"], float)

def test_study_session():
    """Test study session state."""
    session: StudySession = {
        "session_id": "sess_1",
        "topic": "Python Basics",
        "course_id": "CS101",
        "start_time": datetime.now(),
        "duration": 60.0,
        "objectives": ["Learn variables", "Learn functions"],
        "materials": ["textbook", "slides"],
        "notes": ["Important concept: variables"]
    }
    
    assert isinstance(session, dict)
    assert isinstance(session["duration"], float)
    assert len(session["objectives"]) == 2

def test_learning_progress():
    """Test learning progress state."""
    progress: LearningProgress = {
        "course_id": "CS101",
        "topics": {"variables": 0.8, "functions": 0.6},
        "assessments": [{"quiz_1": "passed"}],
        "strengths": ["problem-solving"],
        "weaknesses": ["theory"],
        "recommendations": ["Practice more theory"]
    }
    
    assert isinstance(progress, dict)
    assert isinstance(progress["topics"], dict)
    assert len(progress["strengths"]) == 1

def test_academic_state():
    """Test complete academic state."""
    state: AcademicState = {
        "messages": [HumanMessage(content="Hello")],
        "profile": {
            "student_id": "12345",
            "name": "John Doe",
            "academic_level": "undergraduate",
            "major": "Computer Science",
            "courses": ["CS101"],
            "preferences": {}
        },
        "calendar": {},
        "tasks": {},
        "study_sessions": {},
        "progress": {},
        "results": {},
        "metrics": {},
        "recommendations": [],
        "errors": [],
        "warnings": []
    }
    
    assert isinstance(state, dict)
    assert "profile" in state
    assert len(state["messages"]) == 1

def test_agent_state():
    """Test academic agent state."""
    agent_state: AgentState = {
        "agent_id": "tutor_1",
        "agent_type": "tutor",
        "status": "active",
        "capabilities": ["python_tutoring", "code_review"],
        "context": {"student_level": "beginner"},
        "memory": {"past_sessions": []},
        "results": {},
        "errors": []
    }
    
    assert isinstance(agent_state, dict)
    assert agent_state["agent_type"] == "tutor"
    assert len(agent_state["capabilities"]) == 2

def test_interaction_state():
    """Test interaction state."""
    interaction: InteractionState = {
        "session_id": "int_1",
        "start_time": datetime.now(),
        "interaction_type": "tutoring",
        "context": {"topic": "Python"},
        "history": [{"action": "question", "time": datetime.now()}],
        "objectives": ["Learn Python basics"],
        "progress": {"completed_topics": 1},
        "current_focus": "variables"
    }
    
    assert isinstance(interaction, dict)
    assert interaction["interaction_type"] == "tutoring"
    assert len(interaction["objectives"]) == 1

def test_state_composition():
    """Test composing different states together."""
    # Create initial state
    initial_state: AcademicState = {
        "messages": [],
        "profile": {
            "student_id": "12345",
            "name": "John Doe",
            "academic_level": "undergraduate",
            "major": "CS",
            "courses": ["CS101"],
            "preferences": {}
        },
        "calendar": {},
        "tasks": {},
        "study_sessions": {},
        "progress": {},
        "results": {"quiz_1": "pending"},
        "metrics": {},
        "recommendations": [],
        "errors": [],
        "warnings": []
    }
    
    # Create update
    update = {
        "results": {"quiz_1": "passed"},
        "metrics": {"study_time": 60},
        "recommendations": [{"topic": "Practice more"}]
    }
    
    # Merge states
    final_state = dict_reducer(initial_state, update)
    
    assert final_state["results"]["quiz_1"] == "passed"
    assert final_state["metrics"]["study_time"] == 60
    assert len(final_state["recommendations"]) == 1
    assert final_state["profile"]["name"] == "John Doe"  # Original data preserved 