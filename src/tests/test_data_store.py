import pytest
from typing import Dict, Any
from src.data.manager import DataStore, MemoryStore

@pytest.fixture
def sample_data() -> Dict[str, Any]:
    """Create sample data for testing."""
    return {
        "key1": {"value": "test1"},
        "key2": {"value": "test2"}
    }

class TestMemoryStore:
    """Test suite for MemoryStore implementation."""
    
    @pytest.fixture
    def memory_store(self):
        """Create a memory store instance for testing."""
        return MemoryStore()

    @pytest.mark.asyncio
    async def test_store_and_retrieve(self, memory_store: MemoryStore, sample_data):
        """
        Test basic store and retrieve functionality.
        Verifies:
        - Data can be stored successfully
        - Retrieved data matches stored data
        - Multiple key-value pairs can be stored
        """
        # Store multiple items
        for key, value in sample_data.items():
            await memory_store.store(key, value)
        
        # Retrieve and verify each item
        for key, expected_value in sample_data.items():
            retrieved_value = await memory_store.retrieve(key)
            assert retrieved_value == expected_value

    @pytest.mark.asyncio
    async def test_retrieve_nonexistent(self, memory_store: MemoryStore):
        """
        Test retrieving non-existent key.
        Verifies:
        - None is returned for non-existent keys
        - No exception is raised
        """
        result = await memory_store.retrieve("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self, memory_store: MemoryStore, sample_data):
        """
        Test delete functionality.
        Verifies:
        - Data can be deleted
        - Deleted data cannot be retrieved
        - Deleting non-existent key doesn't raise error
        """
        # Store and then delete
        key, value = next(iter(sample_data.items()))
        await memory_store.store(key, value)
        await memory_store.delete(key)
        
        # Verify deletion
        result = await memory_store.retrieve(key)
        assert result is None
        
        # Delete non-existent key
        await memory_store.delete("nonexistent")  # Should not raise

    @pytest.mark.asyncio
    async def test_update_existing(self, memory_store: MemoryStore):
        """
        Test updating existing data.
        Verifies:
        - Existing data can be updated
        - Retrieved data reflects updates
        """
        key = "test_key"
        initial_value = {"data": "initial"}
        updated_value = {"data": "updated"}
        
        # Store initial value
        await memory_store.store(key, initial_value)
        
        # Update value
        await memory_store.store(key, updated_value)
        
        # Verify update
        result = await memory_store.retrieve(key)
        assert result == updated_value

    @pytest.mark.asyncio
    async def test_store_different_types(self, memory_store: MemoryStore):
        """
        Test storing different data types.
        Verifies:
        - Different Python types can be stored and retrieved
        - Data integrity is maintained for different types
        """
        test_data = {
            "string_key": "string_value",
            "int_key": 42,
            "float_key": 3.14,
            "list_key": [1, 2, 3],
            "dict_key": {"nested": "value"},
            "bool_key": True,
            "none_key": None
        }
        
        # Store all types
        for key, value in test_data.items():
            await memory_store.store(key, value)
        
        # Verify all types
        for key, expected_value in test_data.items():
            result = await memory_store.retrieve(key)
            assert result == expected_value
            assert type(result) == type(expected_value)

class TestDataStoreInterface:
    """
    Test suite for DataStore interface implementation requirements.
    These tests ensure any DataStore implementation follows the contract.
    """
    
    class MinimalDataStore(DataStore):
        """Minimal implementation of DataStore for testing."""
        async def store(self, key: str, data: Dict[str, Any]) -> None:
            pass
            
        async def retrieve(self, key: str) -> Dict[str, Any]:
            return {}
            
        async def delete(self, key: str) -> None:
            pass

    def test_interface_implementation(self):
        """
        Test that implementing DataStore interface is possible.
        Verifies:
        - Interface can be implemented
        - Required methods are present
        """
        store = self.MinimalDataStore()
        assert isinstance(store, DataStore)
        
        # Verify required methods exist
        assert hasattr(store, 'store')
        assert hasattr(store, 'retrieve')
        assert hasattr(store, 'delete') 