import pytest
from typing import Dict, Any, List
from src.agents.coordinator import ReActCoordinator
from src.agents.models.coordination import (
    ProfileData, ContextAnalysis, RequestType,
    ComplexityLevel, CoordinationPlan, ReActTrace,
    ReActStep, ValidationResult
)
from src.agents.coordinator.utils import ContextAnalyzer