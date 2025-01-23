# ATHENA Project Overview

## Description
ATHENA is an agentic-AI academic assistance application designed to revolutionize learning for anyone and everyone.
ATHENA utilizes a multi-agent system to provide adaptive, personalized, and context-aware learning assistance to users.
This includes everything from creating learning plans, progress tracking, and feedback systems to recommending personalized study materials and resources.

## Core Components
- Academic State Management
- Student Profile Handling
- Task and Calendar Management
- Progress Tracking
- Learning Resource Management
- Feedback System

## Technical Overview
- Multi-Agent System and Collaboration: agents with distinct roles such as coordination, planning, execution, feedback, evaluation, and more.
- Retrieval Augmented Generation (RAG): Leveraging external knowledge sources to enhance agent capabilities and provide more accurate and relevant information using information stored in vector databases.
- Agentic Architecture: Agents with distinct roles such as coordination, planning, execution, feedback, evaluation, and more.
- Web Search, Scraping and Retrieval: A general purpose web search and scraping agent that can be used to retrieve information from the web while handling both static and dynamic content, including Javascript-heavy websites.
- Dynamic Data Handling: Supporting both structured and unstructured data from diverse sources.
- Output Management: Storing outputs in JSON format by default with the option to integrate results into databases and vector stores.

## Project Requirements and Directives
### 1. Multi-Agent System Design
### Requirements
### - Agent Roles:
    - Coordinator Agent: Oversees task delegation and ensures agents collaborate effectively.
    - Planning Agent(s): Breaks down user queries into sub-tasks and assigns.
    - Retriever Agent(s): Queries vector databases or external tools to fetch relevant information.`
    - Tool-Use Agent(s): Executes specific tasks like web scraping, API calls, or calculatios
    - Feedback Agent(s): Provides feedback on learner performance, offering personalized guidance and support.

### Framework
    - use `langchain` and `langgraph` for agent workflows and enable tool integrations 
    - implement modular agents that can be easily reused, extended for new tasks, or replaced with new agents if necessary.

### Directives: 
    - Design agents to operate autonomously for their own tasks but also be able to coordinate with other agents to complete more complex tasks through the coordinator agent.
    - Use Pydantic for structured outputs and intermediate input-output flow to ensure consistency and reliability across agents.
    - Implement logging and debugging tools to monitor inter-agent communication.

### 2. Retrieval-Augmented Generation (RAG)
### Requirements
### - Knowldge Sources:
    - Structuredd Data: SQL databases or APIs
    - Unstructured Data: Documents, Web pages, PDFs, etc., stored in vector databases.
### - Vector Database: 
    - Use Redis or Weaviate for vector storage and retrieval. (for local development). 
    - Consider pinecone later for cloud deployment and scalability if needed. 

### Directives
    - Start with a simpler RAG pipeline where retrieval logic is centralized. 
    - Transition to an agentic RAG pipeline where individual agents can dynamically decide how to retrieve data based on their individual contexts and requirements. This approach is contingent on a regular RAG pipeline (or cluster) not being adequate for the multi-agent system.
    - Ensure embeddinfs are generated using a robust model.

### 3. Web Search, Scraping, and Retrieval
### Requirements
### - General Purpose Web Search and Scraping Tool capable of:
    - Search using Travily search API for web search.

### 4. Dynamic Data Handling
### Requirements
- Support diverse data formats:
    - Structured Data
    - Unstructured Data
- Enable agents to dynamically decide how to process incoming data based on its type. 
### Directives
- use file parsers like `pandas` for csvs, `PyPDF2` for PDFs, `bs4` for HTML, etc., to preprocess data before ingestion into the system.
- Normalize all processed data into JSON format for consistency across workflows.

### - Ability to handle large datasets and perform efficient data processing and analysis.
### - Integration with existing data systems and databases.

### Directives


## Architecture
- `src/utils/`: Core utilities and state management
- `src/agents/`: AI agent implementations
- `src/data/`: Data management and storage
- `src/tests/`: Test suites
- `src/api/`: API endpoints
- `src/rag/`: Retrieval-augmented generation components 
- 