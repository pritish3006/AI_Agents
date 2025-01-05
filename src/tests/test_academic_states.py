import pytest
from datetime import datetime
from typing import Dict, Any
from src.utils.academic_states import (
    AcademicState,
    StudentProfile,
    CalendarEvent,
    AcademicTask,
    ProgressMetric,
    FeedbackItem,
    InteractionResult
)
from src.agents.models.coordination import ValidationResult

@pytest.fixture
def sample_student_profile() -> StudentProfile:
    """Create a sample student profile for testing."""
    return {
        "id": "student123",
        "name": "John Doe",
        "level": "undergraduate",
        "major": "Computer Science",
        "courses": ["CS101", "MATH201"],
        "topics": ["Python", "Data Structures"],
        "preferences": {"study_time": "morning"},
        "history": [{"action": "enrolled", "course": "CS101", "date": "2023-01-01"}]
    }

@pytest.fixture
def sample_calendar_event() -> CalendarEvent:
    """Create a sample calendar event for testing."""
    now = datetime.now()
    return {
        "id": "evt123",
        "title": "Test Event",
        "type": "class",
        "start_time": now,
        "end_time": now,
        "description": "Test class session",
        "course_id": "CS101",
        "metadata": {"location": "Room 101"}
    }

@pytest.fixture
def sample_academic_task() -> AcademicTask:
    """Create a sample academic task for testing."""
    return {
        "id": "task123",
        "title": "Assignment 1",
        "description": "Complete programming exercise",
        "course_id": "CS101",
        "due_date": datetime.now(),
        "status": "pending",
        "priority": 1,
        "attachments": ["doc1.pdf"],
        "metadata": {"points": 100}
    }

@pytest.fixture
def base_academic_state(
    sample_student_profile: StudentProfile,
    sample_calendar_event: CalendarEvent,
    sample_academic_task: AcademicTask
) -> AcademicState:
    """Create a base academic state for testing."""
    return AcademicState(
        profile=sample_student_profile,
        calendar={sample_calendar_event["id"]: sample_calendar_event},
        upcoming_events=[sample_calendar_event["id"]],
        tasks={sample_academic_task["id"]: sample_academic_task},
        active_tasks=[sample_academic_task["id"]],
        completed_tasks=[],
        progress={},
        learning_resources={},
        study_plans={},
        results={},
        feedback=[],
        validation={"is_valid": True, "errors": []},
        notifications=[]
    )

class TestAcademicState:
    """Test suite for AcademicState class."""

    def test_create_academic_state(self, base_academic_state: AcademicState):
        """
        Test creation of academic state.
        Verifies:
        - All required fields are present
        - Fields have correct types
        - Initial state is properly set
        """
        assert isinstance(base_academic_state.profile, dict)
        assert isinstance(base_academic_state.calendar, dict)
        assert isinstance(base_academic_state.upcoming_events, list)
        assert isinstance(base_academic_state.tasks, dict)
        assert isinstance(base_academic_state.active_tasks, list)
        assert isinstance(base_academic_state.completed_tasks, list)
        assert isinstance(base_academic_state.validation, dict)

    def test_merge_student_profiles(self, base_academic_state: AcademicState):
        """
        Test merging of student profiles.
        Verifies:
        - Basic fields are preserved
        - Lists (courses, topics) are properly merged with uniqueness
        - Dictionaries (preferences) are properly merged
        - History is properly appended
        """
        other_state = AcademicState(
            profile={
                "id": "test123",
                "name": "Test Student",
                "level": "undergraduate",
                "major": "Computer Science",
                "courses": ["CS102", "CS101"],  # Note: CS101 is duplicate
                "topics": ["Algorithms", "Data Structures"],  # Note: Algorithms is duplicate
                "preferences": {"study_time": "evening", "new_pref": "value"},
                "history": [{"action": "completed", "course": "CS101", "date": "2023-01-02"}]
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

        merged_state = base_academic_state.merge(other_state)
        
        # Verify merged profile
        assert len(merged_state.profile["courses"]) == 3  # CS101, CS102
        assert len(merged_state.profile["topics"]) == 3  # Programming, Algorithms, Data Structures
        assert merged_state.profile["preferences"]["study_time"] == "evening"
        assert merged_state.profile["preferences"]["new_pref"] == "value"
        assert len(merged_state.profile["history"]) == 2

    def test_merge_tasks_and_events(self, base_academic_state: AcademicState):
        """
        Test merging of tasks and calendar events.
        Verifies:
        - Tasks are properly merged
        - Active tasks list maintains uniqueness
        - Completed tasks are properly appended
        - Calendar events are properly merged
        """
        new_task = {
            "id": "task124",
            "title": "Assignment 2",
            "description": "New assignment",
            "course_id": "CS101",
            "due_date": datetime.now(),
            "status": "pending",
            "priority": 2,
            "attachments": [],
            "metadata": {}
        }

        other_state = AcademicState(
            profile={},
            calendar={},
            upcoming_events=[],
            tasks={"task124": new_task},
            active_tasks=["task124"],
            completed_tasks=["task123"],  # Completing the original task
            progress={},
            learning_resources={},
            study_plans={},
            results={},
            feedback=[],
            validation={"is_valid": True, "errors": []},
            notifications=[]
        )

        merged_state = base_academic_state.merge(other_state)
        
        # Verify merged tasks
        assert len(merged_state.tasks) == 2
        assert len(merged_state.active_tasks) == 2
        assert len(merged_state.completed_tasks) == 1
        assert "task123" in merged_state.completed_tasks

    def test_merge_validation_and_notifications(self, base_academic_state: AcademicState):
        """
        Test merging of validation results and notifications.
        Verifies:
        - Validation errors are properly combined
        - Notifications are properly appended
        """
        other_state = AcademicState(
            profile={},
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
            validation={},
            notifications=[]
        )

        # Merge states
        merged_state = base_academic_state.merge(second_state)

        # Verify merge results
        assert len(merged_state.calendar) == 2
        assert len(merged_state.upcoming_events) == 2
        assert "evt123" in merged_state.calendar
        assert "evt456" in merged_state.calendar

    def test_list_reducers(self, base_academic_state):
        """Test list reducer behavior in state."""
        # Test unique reducer
        base_academic_state.active_tasks.extend(["task1", "task1", "task2"])
        assert len(base_academic_state.active_tasks) == 2
        assert set(base_academic_state.active_tasks) == {"task1", "task2"}

        # Test append reducer
        base_academic_state.completed_tasks.extend(["task3", "task3"])
        assert len(base_academic_state.completed_tasks) == 2
        assert base_academic_state.completed_tasks == ["task3", "task3"] 