# AI Learning Agent System

A sophisticated multi-agent system designed to provide personalized learning support using advanced language models and RAG pipelines. This project is inspired by the ATLAS (Academic Task and Learning Agent System) architecture and uses LangGraph for workflow orchestration.

## Project Structure
```
src/
├── agents/         # Agent implementations using LangGraph
├── api/           # FastAPI endpoints
├── rag/           # RAG pipeline implementation
├── config/        # Configuration files
├── utils/         # Utility functions
└── tests/         # Test files
```

## Setup

### Option 1: Using Conda (Recommended)
1. Create a conda environment:
```bash
conda create -n ai-learning-agent python=3.12
conda activate ai-learning-agent
```

2. For zsh users, add conda initialization to ~/.zshrc:
```bash
# Add these lines to your ~/.zshrc
eval "$(conda shell.zsh hook)"
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Option 2: Using venv
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. For zsh users, you can add this to your ~/.zshrc for quick activation:
```bash
# Add this to your ~/.zshrc
alias venv-activate="source venv/bin/activate"
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file in the root directory with the following variables:
```
API_KEY=your_api_key
PINECONE_API_KEY=your_pinecone_key
ENVIRONMENT=development
```

## Development
- Follow the development plan in `dev_plan.txt`
- Run tests: `pytest`
- Start API server: `uvicorn src.api.main:app --reload`

## Architecture
The system uses LangGraph for workflow orchestration, enabling:
- Coordinated multi-agent interactions
- State management across agent workflows
- Structured communication patterns
- Dynamic task allocation and execution

## Docker
Docker setup instructions will be added in the next phase. 