# import pytest
# from datetime import datetime, timezone, timedelta
# import json
# from src.data.academic_manager import (
#     AcademicDataManager,
#     MemoryStore,
#     DataStore,
#     DataValidationError
# )
# from src.utils.academic_states import StudentProfile, CalendarEvent, AcademicTask
# 
# class MockStore(DataStore):
#     """Mock data store for testing."""
#     def __init__(self, should_fail: bool = False):
#         self._store = {}
#         self.should_fail = should_fail
#     
#     async def store(self, key: str, data: Dict[str, Any]) -> None:
#         if self.should_fail:
#             raise Exception("Mock store failure")
#         self._store[key] = data
#     
#     async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
#         if self.should_fail:
#             raise Exception("Mock store failure")
#         return self._store.get(key)
#     
#     async def delete(self, key: str) -> None:
#         if self.should_fail:
#             raise Exception("Mock store failure")
#         self._store.pop(key, None)
# 
# @pytest.fixture
# def data_manager():
#     """Create a test instance of AcademicDataManager."""
#     return AcademicDataManager(store=MemoryStore())
# 
# @pytest.fixture
# def failing_data_manager():
#     """Create a test instance of AcademicDataManager with failing store."""
#     return AcademicDataManager(store=MockStore(should_fail=True))
# 
# @pytest.fixture
# def sample_profile():
#     """Create a sample student profile."""
#     return {
#         "id": "test123",
#         "name": "Test Student",
#         "level": "undergraduate",
#         "major": "Computer Science",
#         "courses": ["CS101", "MATH201"],
#         "topics": ["python", "algorithms"],
#         "preferences": {"study_time": "morning"},
#         "history": []
#     }
# 
# @pytest.fixture
# def sample_calendar():
#     """Create sample calendar events."""
#     now = datetime.now(timezone.utc)
#     return {
#         "events": [
#             {
#                 "id": "evt1",
#                 "title": "CS101 Lecture",
#                 "type": "class",
#                 "start_time": (now + timedelta(days=1)).isoformat(),
#                 "end_time": (now + timedelta(days=1, hours=1)).isoformat(),
#                 "description": "Introduction to Python",
#                 "course_id": "CS101",
#                 "metadata": {}
#             },
#             {
#                 "id": "evt2",
#                 "title": "MATH201 Quiz",
#                 "type": "exam",
#                 "start_time": (now + timedelta(days=2)).isoformat(),
#                 "end_time": (now + timedelta(days=2, hours=2)).isoformat(),
#                 "description": "Linear Algebra Quiz",
#                 "course_id": "MATH201",
#                 "metadata": {}
#             }
#         ]
#     }
# 
# @pytest.fixture
# def sample_tasks():
#     """Create sample academic tasks."""
#     now = datetime.now(timezone.utc)
#     return {
#         "tasks": [
#             {
#                 "id": "task1",
#                 "title": "Python Assignment",
#                 "description": "Complete exercises 1-5",
#                 "course_id": "CS101",
#                 "due_date": (now + timedelta(days=3)).isoformat(),
#                 "status": "pending",
#                 "priority": 1,
#                 "attachments": [],
#                 "metadata": {}
#             },
#             {
#                 "id": "task2",
#                 "title": "Math Homework",
#                 "description": "Solve problems from Chapter 3",
#                 "course_id": "MATH201",
#                 "due_date": (now + timedelta(days=4)).isoformat(),
#                 "status": "pending",
#                 "priority": 2,
#                 "attachments": [],
#                 "metadata": {}
#             }
#         ]
#     }
# 
# @pytest.mark.asyncio
# async def test_load_data(data_manager, sample_profile, sample_calendar, sample_tasks):
#     """Test loading data from multiple sources."""
#     result = await data_manager.load_data(
#         profile_data=sample_profile,
#         calendar_data=sample_calendar,
#         task_data=sample_tasks
#     )
#     
#     assert result.is_valid
#     assert not result.errors
#     
#     # Verify profile was stored
#     profile = await data_manager.get_learner_profile("test123")
#     assert profile is not None
#     assert profile["name"] == "Test Student"
# 
# @pytest.mark.asyncio
# async def test_load_invalid_data(data_manager):
#     """Test loading invalid data."""
#     invalid_profile = {"invalid": "data"}
#     result = await data_manager.load_data(
#         profile_data=invalid_profile,
#         calendar_data={},
#         task_data={}
#     )
#     
#     assert not result.is_valid
#     assert len(result.errors) > 0
# 
# @pytest.mark.asyncio
# async def test_store_failure(failing_data_manager, sample_profile):
#     """Test handling of storage failures."""
#     with pytest.raises(DataValidationError):
#         await failing_data_manager._store_profile(sample_profile)
# 
# @pytest.mark.asyncio
# async def test_get_learner_profile(data_manager, sample_profile):
#     """Test retrieving learner profile."""
#     # Load initial data
#     await data_manager.load_data(
#         profile_data=sample_profile,
#         calendar_data={"events": []},
#         task_data={"tasks": []}
#     )
#     
#     # Test cache hit
#     profile1 = await data_manager.get_learner_profile("test123")
#     assert profile1 is not None
#     assert profile1["name"] == "Test Student"
#     
#     # Clear cache and test store retrieval
#     data_manager._profile_cache.clear()
#     profile2 = await data_manager.get_learner_profile("test123")
#     assert profile2 is not None
#     assert profile2["name"] == "Test Student"
# 
# def test_parse_datetime(data_manager):
#     """Test datetime parsing functionality."""
#     # Test UTC timezone
#     dt_str = "2024-01-01T12:00:00Z"
#     dt = data_manager.parse_datetime(dt_str)
#     assert dt.tzinfo == timezone.utc
#     
#     # Test naive datetime
#     dt_str = "2024-01-01T12:00:00"
#     dt = data_manager.parse_datetime(dt_str)
#     assert dt.tzinfo == timezone.utc
#     
#     # Test different timezone
#     dt_str = "2024-01-01T12:00:00+05:00"
#     dt = data_manager.parse_datetime(dt_str)
#     assert dt.tzinfo == timezone.utc
#     
#     # Test invalid format
#     with pytest.raises(ValueError):
#         data_manager.parse_datetime("invalid")
# 
# @pytest.mark.asyncio
# async def test_upcoming_calendar_events(data_manager, sample_profile, sample_calendar):
#     """Test retrieving upcoming calendar events."""
#     # Load initial data
#     await data_manager.load_data(
#         profile_data=sample_profile,
#         calendar_data=sample_calendar,
#         task_data={"tasks": []}
#     )
#     
#     # Get upcoming events
#     events = await data_manager.upcoming_calendar_events("test123", days_ahead=7)
#     assert len(events) == 2
#     assert events[0]["title"] == "CS101 Lecture"
#     assert events[1]["title"] == "MATH201 Quiz"
#     
#     # Test with shorter timeframe
#     events = await data_manager.upcoming_calendar_events("test123", days_ahead=1)
#     assert len(events) == 1
#     assert events[0]["title"] == "CS101 Lecture"
# 
# @pytest.mark.asyncio
# async def test_get_active_tasks(data_manager, sample_profile, sample_tasks):
#     """Test retrieving active tasks."""
#     # Load initial data
#     await data_manager.load_data(
#         profile_data=sample_profile,
#         calendar_data={"events": []},
#         task_data=sample_tasks
#     )
#     
#     # Get active tasks
#     tasks = await data_manager.get_active_tasks("test123")
#     assert len(tasks) == 2
#     assert tasks[0]["title"] == "Python Assignment"
#     assert tasks[1]["title"] == "Math Homework"
#     
#     # Modify task status and test again
#     data_manager._task_cache["test123"][0]["status"] = "completed"
#     tasks = await data_manager.get_active_tasks("test123")
#     assert len(tasks) == 1
#     assert tasks[0]["title"] == "Math Homework"
# 
# @pytest.mark.asyncio
# async def test_cache_invalidation(data_manager, sample_profile):
#     """Test cache invalidation based on TTL."""
#     # Load initial data
#     await data_manager.load_data(
#         profile_data=sample_profile,
#         calendar_data={"events": []},
#         task_data={"tasks": []}
#     )
#     
#     # Manually expire cache
#     data_manager._cache_timestamps["profile_test123"] = (
#         datetime.now(timezone.utc) - timedelta(seconds=data_manager._cache_ttl + 1)
#     )
#     
#     # Should trigger a store retrieval
#     profile = await data_manager.get_learner_profile("test123")
#     assert profile is not None
#     assert profile["name"] == "Test Student"
# 
# @pytest.mark.asyncio
# async def test_cleanup(data_manager, sample_profile, sample_calendar, sample_tasks):
#     """Test resource cleanup."""
#     # Load data
#     await data_manager.load_data(
#         profile_data=sample_profile,
#         calendar_data=sample_calendar,
#         task_data=sample_tasks
#     )
#     
#     # Verify caches are populated
#     assert len(data_manager._profile_cache) > 0
#     assert len(data_manager._calendar_cache) > 0
#     assert len(data_manager._task_cache) > 0
#     assert len(data_manager._cache_timestamps) > 0
#     
#     # Cleanup
#     await data_manager.cleanup()
#     
#     # Verify caches are cleared
#     assert len(data_manager._profile_cache) == 0
#     assert len(data_manager._calendar_cache) == 0
#     assert len(data_manager._task_cache) == 0
#     assert len(data_manager._cache_timestamps) == 0