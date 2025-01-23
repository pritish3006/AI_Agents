import pytest
from datetime import datetime, timezone
from typing import Dict, Any
from src.utils.academic_states import (
    AcademicState,
    StudentProfile,
    CalendarEvent,
    AcademicTask
)
from src.data.manager import DataManager, MemoryStore

@pytest.fixture
async def memory_store():
    """Create a memory store instance for testing."""
    store = MemoryStore()
    return store

@pytest.fixture
async def data_manager(memory_store):
    """Create a data manager instance for testing."""
    store = await memory_store
    return DataManager(store=store)

@pytest.fixture
def sample_student_data() -> Dict[str, Any]:
    """Create sample student data for testing."""
    now = datetime.now(timezone.utc)
    return {
        "profile": {
            "id": "student123",
            "name": "Test Student",
            "level": "undergraduate",
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
                    "metadata": {}
                }
            ]
        },
        "tasks": {
            "tasks": [
                {
                    "id": "task123",
                    "title": "Assignment 1",
                    "description": "Complete programming exercise",
                    "due_date": now,
                    "status": "pending",
                    "priority": 1,
                    "attachments": [],
                    "metadata": {}
                }
            ]
        }
    }

class TestSystemIntegration:
    """Integration tests for the system components."""

    @pytest.mark.asyncio
    async def test_student_data_flow(
        self,
        data_manager: DataManager,
        sample_student_data: Dict[str, Any]
    ):
        """Test the complete flow of student data through the system."""
        student_id = sample_student_data["profile"]["id"]

        # Store initial state
        success = await data_manager.load_data(
            profile_data=sample_student_data["profile"],
            calendar_data=sample_student_data["calendar"],
            task_data=sample_student_data["tasks"]
        )
        assert success is True

        # Retrieve and verify state
        profile = await data_manager.get_profile(student_id)
        calendar = await data_manager.get_calendar(student_id)
        tasks = await data_manager.get_tasks(student_id)

        assert profile is not None
        assert profile.name == "Test Student"
        assert profile.level == "undergraduate"
        assert len(profile.courses) == 2
        assert "CS101" in profile.courses

        assert len(calendar) == 1
        assert calendar[0].title == "CS101 Lecture"
        assert calendar[0].type == "class"

        assert len(tasks) == 1
        assert tasks[0].title == "Assignment 1"
        assert tasks[0].status == "pending"

    @pytest.mark.asyncio
    async def test_concurrent_updates(
        self,
        data_manager: DataManager,
        sample_student_data: Dict[str, Any]
    ):
        """Test handling of concurrent updates."""
        student_id = sample_student_data["profile"]["id"]
        
        # Store initial state
        success = await data_manager.load_data(
            profile_data=sample_student_data["profile"],
            calendar_data=sample_student_data["calendar"],
            task_data=sample_student_data["tasks"]
        )
        assert success is True
        
        # Update profile with new courses
        updated_profile = dict(sample_student_data["profile"])
        updated_profile["courses"].append("CS102")
        
        # Store updates
        success = await data_manager.load_data(
            profile_data=updated_profile,
            calendar_data={},
            task_data={}
        )
        assert success is True
        
        # Verify updates
        final_profile = await data_manager.get_profile(student_id)
        assert final_profile is not None
        assert "CS102" in final_profile.courses
        assert len(final_profile.courses) == 3

    @pytest.mark.asyncio
    async def test_error_handling(
        self,
        data_manager: DataManager,
        sample_student_data: Dict[str, Any]
    ):
        """Test error handling in the system."""
        student_id = sample_student_data["profile"]["id"]
        
        # Store initial state
        success = await data_manager.load_data(
            profile_data=sample_student_data["profile"],
            calendar_data=sample_student_data["calendar"],
            task_data=sample_student_data["tasks"]
        )
        assert success is True
        
        # Try invalid data
        invalid_profile = dict(sample_student_data["profile"])
        invalid_profile["id"] = None  # This should fail validation
        
        result = await data_manager.load_data(
            profile_data=invalid_profile,
            calendar_data={},
            task_data={}
        )
        assert result is False  # Should return False for invalid data
        
        # Verify original state preserved
        profile = await data_manager.get_profile(student_id)
        assert profile is not None
        assert profile.id == student_id  # Original data should be preserved 