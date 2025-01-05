from typing import Dict, Any, List, Optional, Union, Protocol
from datetime import datetime, timezone
import json
from pydantic import ValidationError
from src.utils.academic_states import StudentProfile, CalendarEvent, AcademicTask

class DataStore(Protocol):
    """protocol for data storage implementations"""
    async def store(self, key: str, data: Dict[str, Any]) -> None:
        """store data with given key"""
        ... # abstract method

    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]: 
        """retrieve data for given key"""
        ... # abstract method

    async def delete(self, key: str) -> None:
        """delete data for given key"""
        ... # abstract method

class MemoryStore(DataStore):
    """in-memory implementation of the DataStore protocol"""
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    async def store(self, key: str, data: Dict[str, Any]) -> None:
        self._store[key] = data
    
    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        return self._store.get(key)
    
    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

class DataValidationError(Exception):
    """custom exception for data validation errors"""
    def __init__(self, message: str, details: Dict[str, Any]):
        self.message = message
        self.details = details
        super().__init__(message)

class DataManager:
    """
    centralized data manager for all data operations. 
    handles data loading, parsing, and retrieval with proper validation and error handling. 
    this class includes: 
    - loading and parsing of data from various sources.
    - retrieving the user's profile, calendar, and tasks.
    - storing and retrieving agent states for persistence.
    - data validation and error handling.
    - caching mechanisms for performance optimization.
    """

    def __init__(self, store: Optional[DataStore] = None):
        self.store = store or MemoryStore()

    async def load_data(
        self,
        profile_data: Union[str, Dict],
        calendar_data: Union[str, Dict],
        task_data: Union[str, Dict]
    ) -> bool:
        """
        load data from various sources and validate them

        Args:
            profile_data: JSON string or dict containing user profile data
            calendar_data: JSON string or dict containing calendar data
            task_data: JSON string or dict containing task data

        Returns:
            bool: True if data is loaded and validated successfully, False otherwise
        """
        try:
            # Parse JSON if needed
            profile = profile_data if isinstance(profile_data, dict) else json.loads(profile_data)
            calendar = calendar_data if isinstance(calendar_data, dict) else json.loads(calendar_data)
            tasks = task_data if isinstance(task_data, dict) else json.loads(task_data)

            # Debug print
            print(f"Input profile data: {profile}")

            # Validate data structure
            if "events" not in calendar:
                calendar["events"] = []
            if "tasks" not in tasks:
                tasks["tasks"] = []

            # Validate and create models
            student_profile = StudentProfile(**profile)
            events = [CalendarEvent(**event) for event in calendar["events"]]
            task_list = [AcademicTask(**task) for task in tasks["tasks"]]

            # Debug print
            print(f"Created profile: {student_profile}")
            # Get profile ID before converting to dict
            profile_id = student_profile.id

            # Store data
            await self.store.store(f"profile_{profile_id}", student_profile.dict())
            await self.store.store(f"calendar_{profile_id}", {"events": [e.dict() for e in events]})
            await self.store.store(f"tasks_{profile_id}", {"tasks": [t.dict() for t in task_list]})

            # Verify storage (debug)
            stored_profile = await self.store.retrieve(f"profile_{profile_id}")
            stored_calendar = await self.store.retrieve(f"calendar_{profile_id}")
            stored_tasks = await self.store.retrieve(f"tasks_{profile_id}")
            
            print(f"Stored profile: {stored_profile}")
            print(f"Stored calendar: {stored_calendar}")
            print(f"Stored tasks: {stored_tasks}")

            return True
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return False
        except ValidationError as e:
            print(f"Validation error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    async def get_profile(self, profile_id: str) -> Optional[StudentProfile]:
        """Get profile data"""
        data = await self.store.retrieve(f"profile_{profile_id}")
        return StudentProfile(**data) if data else None

    async def get_calendar(self, profile_id: str) -> List[CalendarEvent]:
        """Get calendar events"""
        data = await self.store.retrieve(f"calendar_{profile_id}")
        return [CalendarEvent(**event) for event in data.get("events", [])] if data else []

    async def get_tasks(self, profile_id: str) -> List[AcademicTask]:
        """Get tasks"""
        data = await self.store.retrieve(f"tasks_{profile_id}")
        return [AcademicTask(**task) for task in data.get("tasks", [])] if data else []