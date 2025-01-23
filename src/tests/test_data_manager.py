import pytest
from datetime import datetime, timezone, timedelta
import json
from typing import Dict, Any, Optional

from src.data.manager import DataManager, DataStore, MemoryStore
from src.utils.academic_states import StudentProfile, CalendarEvent, AcademicTask

class MockStore(DataStore):
    """Mock data store for testing."""
    def __init__(self, should_fail: bool = False):
        self._store: Dict[str, Dict[str, Any]] = {}
        self.should_fail = should_fail
    
    async def store(self, key: str, data: Dict[str, Any]) -> None:
        if self.should_fail:
            raise Exception("Mock store failure")
        self._store[key] = data
    
    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        if self.should_fail:
            raise Exception("Mock store failure")
        return self._store.get(key)
    
    async def delete(self, key: str) -> None:
        if self.should_fail:
            raise Exception("Mock store failure")
        self._store.pop(key, None)

@pytest.fixture
def data_manager():
    """Create a test instance of DataManager."""
    return DataManager(store=MemoryStore())

@pytest.fixture
def failing_data_manager():
    """Create a test instance of DataManager with failing store."""
    return DataManager(store=MockStore(should_fail=True))

@pytest.fixture
def sample_profile():
    """Create a sample profile for testing."""
    return {
        "id": "test123",
        "name": "Test User",
        "type": "student",
        "learning_goals": ["Python", "ML"],
        "level": "undergraduate",
        "courses": ["Python", "ML"],
        "topics": ["Programming", "Machine Learning"],
        "preferences": {
            "study_time": "morning",
            "session_duration": 60
        },
        "history": []
    }

@pytest.fixture
def sample_calendar():
    """Create sample calendar events for testing."""
    now = datetime.now(timezone.utc)
    return {
        "events": [
            {
                "id": "evt1",
                "title": "Study Session",
                "type": "study",
                "start_time": now,
                "end_time": now,
                "description": "Python Basics",
                "metadata": {}
            }
        ]
    }

@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing."""
    now = datetime.now(timezone.utc)
    return {
        "tasks": [
            {
                "id": "task1",
                "title": "Complete Exercise",
                "description": "Python exercises",
                "due_date": now,
                "status": "pending",
                "priority": 1,
                "attachments": [],
                "metadata": {}
            }
        ]
    }

@pytest.mark.asyncio
class TestDataManager:
    """Test suite for DataManager class."""

    async def test_load_data_dict_input(self, data_manager, sample_profile, sample_calendar, sample_tasks):
        """
        Test load_data with dictionary input.
        Verifies:
        - Loading data from dictionary format
        - Successful validation of all data types
        - Proper storage of all data types
        - Return value is True on success
        """
        result = await data_manager.load_data(
            profile_data=sample_profile,
            calendar_data=sample_calendar,
            task_data=sample_tasks
        )
        assert result is True

        # Verify data was stored correctly
        profile = await data_manager.get_profile("test123")
        assert profile is not None
        assert profile.name == "Test User"

    async def test_load_data_json_input(self, data_manager, sample_profile, sample_calendar, sample_tasks):
        """
        Test load_data with JSON string input.
        Verifies:
        - Loading data from JSON string format
        - JSON parsing functionality
        - Successful validation after parsing
        - Proper storage of parsed data
        """
        result = await data_manager.load_data(
            profile_data=json.dumps(sample_profile),
            calendar_data=json.dumps(sample_calendar),
            task_data=json.dumps(sample_tasks)
        )
        assert result is True

        # Verify data was stored correctly
        profile = await data_manager.get_profile("test123")
        assert profile is not None
        assert profile.name == "Test User"

    async def test_load_data_invalid_json(self, data_manager):
        """
        Test load_data with invalid JSON input.
        Verifies:
        - Proper handling of malformed JSON
        - Return value is False on JSON parsing error
        """
        result = await data_manager.load_data(
            profile_data="{invalid json}",
            calendar_data="{}",
            task_data="{}"
        )
        assert result is False

    async def test_load_data_invalid_schema(self, data_manager, sample_profile, sample_calendar, sample_tasks):
        """
        Test load_data with invalid data schema.
        Verifies:
        - Validation of data structure
        - Handling of invalid field types
        - Return value is False on validation error
        """
        invalid_profile = {**sample_profile}
        invalid_profile["type"] = 123  # Should be string

        result = await data_manager.load_data(
            profile_data=invalid_profile,
            calendar_data=sample_calendar,
            task_data=sample_tasks
        )
        assert result is False

    async def test_get_profile_existing(self, data_manager, sample_profile, sample_calendar, sample_tasks):
        """
        Test get_profile for existing profile.
        Verifies:
        - Retrieval of stored profile
        - Correct conversion to StudentProfile model
        - All fields are preserved
        """
        await data_manager.load_data(sample_profile, sample_calendar, sample_tasks)
        
        profile = await data_manager.get_profile("test123")
        assert profile is not None
        assert profile.id == "test123"
        assert profile.name == "Test User"
        assert profile.type == "student"

    async def test_get_profile_nonexistent(self, data_manager):
        """
        Test get_profile for non-existent profile.
        Verifies:
        - Handling of non-existent profile ID
        - Returns None for missing profile
        """
        profile = await data_manager.get_profile("nonexistent")
        assert profile is None

    async def test_get_calendar_existing(self, data_manager, sample_profile, sample_calendar, sample_tasks):
        """
        Test get_calendar for existing calendar.
        Verifies:
        - Retrieval of stored calendar events
        - Correct conversion to CalendarEvent model
        - All events are preserved
        """
        await data_manager.load_data(sample_profile, sample_calendar, sample_tasks)
        
        events = await data_manager.get_calendar("test123")
        assert len(events) == 1
        assert events[0].id == "evt1"
        assert events[0].title == "Study Session"

    async def test_get_calendar_nonexistent(self, data_manager):
        """
        Test get_calendar for non-existent calendar.
        Verifies:
        - Handling of non-existent profile ID
        - Returns empty list for missing calendar
        """
        events = await data_manager.get_calendar("nonexistent")
        assert len(events) == 0

    async def test_get_tasks_existing(self, data_manager, sample_profile, sample_calendar, sample_tasks):
        """
        Test get_tasks for existing tasks.
        Verifies:
        - Retrieval of stored tasks
        - Correct conversion to AcademicTask model
        - All tasks are preserved
        """
        await data_manager.load_data(sample_profile, sample_calendar, sample_tasks)
        
        tasks = await data_manager.get_tasks("test123")
        assert len(tasks) == 1
        assert tasks[0].id == "task1"
        assert tasks[0].title == "Complete Exercise"
        assert tasks[0].status == "pending"

    async def test_get_tasks_nonexistent(self, data_manager):
        """
        Test get_tasks for non-existent tasks.
        Verifies:
        - Handling of non-existent profile ID
        - Returns empty list for missing tasks
        """
        tasks = await data_manager.get_tasks("nonexistent")
        assert len(tasks) == 0

    async def test_store_failure(self, failing_data_manager, sample_profile, sample_calendar, sample_tasks):
        """
        Test handling of storage failures.
        Verifies:
        - Proper handling of storage errors
        - Return value is False on storage failure
        """
        result = await failing_data_manager.load_data(
            profile_data=sample_profile,
            calendar_data=sample_calendar,
            task_data=sample_tasks
        )
        assert result is False

