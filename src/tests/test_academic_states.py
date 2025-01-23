from src.utils.academic_states import (
    AcademicState, StudentProfile, CalendarEvent, 
    AcademicTask, ProgressMetric, FeedbackItem, InteractionResult
)
import pytest
from datetime import datetime

@pytest.fixture
def base_academic_state():
    """Base fixture with minimal required fields"""
    return AcademicState(
        profile={
            "id": "student456",
            "name": "Jane Smith"
        },
        calendar={},
        upcoming_events=[],
        tasks={},
        active_tasks=[],
        completed_tasks=[],
        progress={},
        learning_resources={},
        study_plans={},
        results={},
        feedback=[],
        validation={"is_valid": True, "errors": []},
        notifications=[]
    )

def test_student_profile_minimal():
    """Test StudentProfile with only required fields"""
    profile: StudentProfile = {
        "id": "student1",
        "name": "John Doe"
    }
    assert profile["id"] == "student1"
    assert profile["name"] == "John Doe"
    assert "level" not in profile
    assert "courses" not in profile

def test_student_profile_full():
    """Test StudentProfile with all fields"""
    profile: StudentProfile = {
        "id": "student1",
        "name": "John Doe",
        "level": "Graduate",
        "major": "Computer Science",
        "courses": ["CS101"],
        "topics": ["Python"],
        "preferences": {"study_time": "morning"},
        "history": [{"completed": "CS100"}]
    }
    assert profile.get("level") == "Graduate"
    assert profile.get("courses") == ["CS101"]

def test_calendar_event():
    """Test CalendarEvent creation"""
    event: CalendarEvent = {
        "id": "evt1",
        "title": "Lecture",
        "type": "class",
        "start_time": datetime.now(),
        "end_time": datetime.now(),
        "description": "CS Lecture",
        "metadata": {}
    }
    assert event["id"] == "evt1"

def test_state_merging(base_academic_state):
    """Test merging of academic states"""
    other_state = AcademicState(
        profile={
            "id": "student123",
            "name": "John Doe",
            "level": None,
            "major": None,
            "courses": ["CS102"],
            "topics": ["Algorithms"],
            "preferences": {},
            "history": []
        },
        calendar={},
        upcoming_events=[],
        tasks={},
        active_tasks=[],
        completed_tasks=["task123"],
        progress={},
        learning_resources={},
        study_plans={},
        results={},
        feedback=[],
        validation={"is_valid": True, "errors": []},
        notifications=[]
    )

    merged = base_academic_state.merge(other_state)
    assert merged.profile["id"] == "student123"
    assert merged.profile["courses"] == ["CS102"]
    assert "task123" in merged.completed_tasks

def test_progress_metrics():
    """Test ProgressMetric creation and validation"""
    metric: ProgressMetric = {
        "metric_type": "grade",
        "value": 95.5,
        "timestamp": datetime.now(),
        "metadata": {"course": "CS101"}
    }
    assert metric["value"] == 95.5

def test_feedback_items():
    """Test FeedbackItem creation"""
    feedback: FeedbackItem = {
        "feedback_type": "suggestion",
        "content": "Great work!",
        "context": {},
        "timestamp": datetime.now()
    }
    assert feedback["feedback_type"] == "suggestion"

def test_academic_task():
    """Test AcademicTask creation"""
    task: AcademicTask = {
        "id": "task1",
        "title": "Assignment 1",
        "description": "Complete homework",
        "due_date": datetime.now(),
        "status": "pending",
        "priority": 1,
        "attachments": [],
        "metadata": {}
    }
    assert task["id"] == "task1"
    assert task["status"] == "pending"

def test_interaction_result():
    """Test InteractionResult creation"""
    result: InteractionResult = {
        "Interaction_type": "quiz",
        "content": {"score": 90},
        "timestamp": datetime.now(),
        "metadata": {}
    }
    assert result["Interaction_type"] == "quiz"

def test_state_list_reducers(base_academic_state):
    """Test list reducers in state merging"""
    other_state = AcademicState(
        profile={"id": "student123", "name": "John"},
        calendar={},
        upcoming_events=["event1"],
        tasks={},
        active_tasks=["task1", "task1"],  # Duplicate to test unique reducer
        completed_tasks=[],
        progress={},
        learning_resources={},
        study_plans={},
        results={},
        feedback=[],
        validation={"is_valid": True, "errors": []},
        notifications=[]
    )
    
    merged = base_academic_state.merge(other_state)
    assert len(merged.active_tasks) == 1  # Tests unique reducer
    assert "event1" in merged.upcoming_events  # Tests append reducer
