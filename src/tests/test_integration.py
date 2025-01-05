import pytest
from datetime import datetime, timezone
from typing import Dict, Any

from src.data.manager import DataManager, MemoryStore
from src.utils.academic_states import (
    StudentProfile, CalendarEvent, AcademicTask, 
    AcademicState
)

@pytest.fixture
def data_manager():
    """Create a DataManager instance with MemoryStore."""
    return DataManager(store=MemoryStore())

@pytest.fixture
def sample_academic_data():
    """Create a complete set of sample academic data."""
    now = datetime.now(timezone.utc)
    
    return {
        "profile": {
            "id": "student123",
            "name": "John Doe",
            "level": "undergraduate",
            "major": "Computer Science",
            "courses": ["CS101", "MATH201"],
            "topics": ["Python", "Data Structures"],
            "preferences": {"study_time": "morning"},
            "history": []
        },
        "calendar": {
            "events": [
                {
                    "id": "evt123",
                    "title": "CS101 Lecture",
                    "type": "class",
                    "start_time": now,
                    "end_time": now,
                    "description": "Introduction to Programming",
                    "course_id": "CS101",
                    "metadata": {"room": "101"}
                }
            ]
        },
        "tasks": {
            "tasks": [
                {
                    "id": "task123",
                    "title": "Complete Assignment 1",
                    "description": "Python basics assignment",
                    "course_id": "CS101",
                    "due_date": now,
                    "status": "pending",
                    "priority": 1,
                    "attachments": [],
                    "metadata": {}
                }
            ]
        }
    }

@pytest.mark.asyncio
class TestDataManagerIntegration:
    """Integration tests for DataManager with other components."""

    async def test_full_academic_workflow(self, data_manager, sample_academic_data):
        """
        Test complete academic workflow from data loading to state management.
        Verifies:
        - Data loading through DataManager
        - Profile retrieval and validation
        - Calendar management
        - Task management
        - State consistency across operations
        """
        # Load all data
        success = await data_manager.load_data(
            profile_data=sample_academic_data["profile"],
            calendar_data=sample_academic_data["calendar"],
            task_data=sample_academic_data["tasks"]
        )
        assert success is True

        # Verify profile data
        profile = await data_manager.get_profile("student123")
        assert profile is not None
        assert profile.name == "John Doe"
        assert "CS101" in profile.courses

        # Verify calendar data
        events = await data_manager.get_calendar("student123")
        assert len(events) == 1
        assert events[0].title == "CS101 Lecture"

        # Verify task data
        tasks = await data_manager.get_tasks("student123")
        assert len(tasks) == 1
        assert tasks[0].title == "Complete Assignment 1"

    async def test_state_persistence(self, data_manager, sample_academic_data):
        """
        Test state persistence across multiple operations.
        Verifies:
        - State is maintained between operations
        - Updates are persistent
        - State is consistent after multiple operations
        """
        # Initial data load
        await data_manager.load_data(
            profile_data=sample_academic_data["profile"],
            calendar_data=sample_academic_data["calendar"],
            task_data=sample_academic_data["tasks"]
        )

        # Modify profile
        profile = await data_manager.get_profile("student123")
        profile.topics.append("Algorithms")
        await data_manager.update_profile("student123", profile)

        # Verify persistence
        updated_profile = await data_manager.get_profile("student123")
        assert "Algorithms" in updated_profile.topics

        # Verify other data remained unchanged
        events = await data_manager.get_calendar("student123")
        assert len(events) == 1
        assert events[0].title == "CS101 Lecture"

    async def test_error_handling(self, data_manager):
        """
        Test error handling in integrated environment.
        Verifies:
        - Invalid data handling
        - Missing data handling
        - Error propagation
        """
        # Test loading invalid profile
        invalid_profile = {"invalid": "data"}
        success = await data_manager.load_data(
            profile_data=invalid_profile,
            calendar_data={},
            task_data={}
        )
        assert success is False

        # Test retrieving non-existent data
        profile = await data_manager.get_profile("nonexistent")
        assert profile is None

        events = await data_manager.get_calendar("nonexistent")
        assert len(events) == 0

        tasks = await data_manager.get_tasks("nonexistent")
        assert len(tasks) == 0

@pytest.mark.asyncio
class TestStateManagerIntegration:
    """Integration tests for State Management with Data Storage."""

    async def test_state_data_store_integration(self, data_manager, sample_academic_data):
        """
        Test integration between state management and data storage.
        Verifies:
        - State changes are properly stored
        - State can be reconstructed from storage
        - State operations affect storage correctly
        """
        # Create initial state
        initial_state = AcademicState(
            profile=sample_academic_data["profile"],
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

        # Store state
        await data_manager.store_state("student123", initial_state)

        # Modify state
        initial_state.active_tasks.append("task1")
        await data_manager.store_state("student123", initial_state)

        # Retrieve and verify state
        retrieved_state = await data_manager.get_state("student123")
        assert retrieved_state is not None
        assert "task1" in retrieved_state.active_tasks

    async def test_concurrent_state_operations(self, data_manager, sample_academic_data):
        """
        Test concurrent state operations.
        Verifies:
        - Multiple state operations can occur concurrently
        - State consistency is maintained under concurrent operations
        - No data corruption occurs during concurrent access
        """
        import asyncio

        # Create initial states
        state1 = AcademicState(
            profile=sample_academic_data["profile"],
            calendar={},
            upcoming_events=[],
            tasks={},
            active_tasks=["task1"],
            completed_tasks=[],
            progress={},
            learning_resources={},
            study_plans={},
            results={},
            feedback=[],
            validation={},
            notifications=[]
        )

        state2 = AcademicState(
            profile=sample_academic_data["profile"],
            calendar={},
            upcoming_events=[],
            tasks={},
            active_tasks=["task2"],
            completed_tasks=[],
            progress={},
            learning_resources={},
            study_plans={},
            results={},
            feedback=[],
            validation={},
            notifications=[]
        )

        # Perform concurrent operations
        await asyncio.gather(
            data_manager.store_state("student1", state1),
            data_manager.store_state("student2", state2)
        )

        # Verify states
        retrieved_state1 = await data_manager.get_state("student1")
        retrieved_state2 = await data_manager.get_state("student2")

        assert "task1" in retrieved_state1.active_tasks
        assert "task2" in retrieved_state2.active_tasks 