# Directory Structure

## Source Code
```
src/
├── agents/                 # AI agent implementations
│   ├── base_agent.py      # Base agent class and interfaces
│   ├── coordinator.py     # Agent coordination logic
│   ├── executor.py        # Task execution agent
│   ├── factory.py         # Agent creation patterns
│   ├── models/           # Agent-specific models
│   │   ├── coordination.py
│   │   └── execution.py
│   ├── react.py          # ReAct pattern implementation
│   └── registry.py       # Agent registration system
│
├── api/                   # API endpoints
│   ├── routes/           # API route definitions
│   ├── middleware/       # API middleware
│   └── models/           # API data models
│
├── data/                 # Data management
│   ├── manager.py       # Core data management
│   └── store/           # Data storage implementations
│
├── rag/                  # Retrieval-augmented generation
│   ├── embeddings/       # Embedding models
│   ├── retriever/        # Content retrieval
│   └── generator/        # Content generation
│
├── tests/               # Test suites
│   ├── conftest.py     # Test configurations
│   ├── test_academic_states.py
│   ├── test_integration.py
│   └── test_react_coordinator.py
│
└── utils/              # Core utilities
    ├── academic_states.py  # Academic state definitions
    ├── reducers.py        # State reduction logic
    └── validators.py      # Data validation utilities
```

## Documentation
```
.notes/
├── project_overview.md      # High-level project description
├── project_directives.md    # Core principles and guidelines
├── project_requirements.md  # Technical and functional requirements
├── project_notes.md        # Current status and decisions
├── task_list.md            # MECE task breakdown
├── task_notes.md           # Implementation details
├── task_requirements.md    # Task-specific requirements
├── meeting_notes.md        # AI interaction log
└── directory_structure.md  # This file
```

## Configuration
```
├── .cursorignore           # Cursor ignore patterns
├── .cursorrules           # Cursor operation rules
├── .gitignore            # Git ignore patterns
├── environment.yml       # Conda environment
├── requirements.txt      # Python dependencies
└── setup.py             # Package setup
```

## Generated
```
├── build/               # Build artifacts
├── dist/               # Distribution packages
├── .pytest_cache/      # Test cache
├── __pycache__/        # Python cache
└── .coverage           # Coverage reports
``` 