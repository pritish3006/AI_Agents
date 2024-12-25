from typing import TypeVar, Dict, Any, List
from typing_extensions import Annotated

T = TypeVar('T')

def dict_reducer(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries recursively.
    
    Example:
    dict1 = {"a": {"x": 1}, "b": 2}
    dict2 = {"a": {"y": 2}, "c": 3}
    result = {"a": {"x": 1, "y": 2}, "b": 2, "c": 3}
    """
    merged = dict1.copy()
    for key, value in dict2.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = dict_reducer(merged[key], value)
        else:
            merged[key] = value
    return merged

def list_append_reducer(list1: List[T], list2: List[T]) -> List[T]:
    """
    Merge two lists by appending list2 to list1.
    Used for maintaining history or sequences.
    
    Example:
    list1 = ["event1", "event2"]
    list2 = ["event3"]
    result = ["event1", "event2", "event3"]
    
    Use cases:
    - Message history
    - Event logs
    - Operation sequences
    """
    return list1 + list2

def list_unique_reducer(list1: List[T], list2: List[T]) -> List[T]:
    """
    Merge two lists maintaining uniqueness.
    Used for sets of unique items.
    
    Example:
    list1 = ["python", "java"]
    list2 = ["java", "golang"]
    result = ["python", "java", "golang"]
    
    Use cases:
    - Capabilities
    - Requirements
    - Resource identifiers
    """
    return list(set(list1 + list2))
