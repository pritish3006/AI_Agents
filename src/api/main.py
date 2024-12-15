from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from src.config import get_app_config
from src.agents import AgentState, AgentFactory, agent_registry
from src.agents.executor import AgentExecutor

# Initialize configuration
config = get_app_config()

# Initialize agent factory and executor
agent_factory = AgentFactory(
    registry=agent_registry,
    config=config,
    dependencies={
        "config": config
    }
)
agent_executor = AgentExecutor(agent_factory)

# Initialize API key security
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

app = FastAPI(
    title=config.PROJECT_NAME,
    description="A sophisticated multi-agent system for different personalized use-cases",
    version=config.VERSION,
    docs_url=None if config.ENVIRONMENT == "production" else "/docs",
    redoc_url=None if config.ENVIRONMENT == "production" else "/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PROD CHECK: In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security dependency
async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

# Request Models
class AgentRequest(BaseModel):
    """Model for agent interaction requests."""
    query: str
    context: Optional[Dict[str, Any]] = None
    agent_type: str = "default"

class ChainRequest(BaseModel):
    """Model for agent chain requests."""
    query: str
    context: Optional[Dict[str, Any]] = None
    agent_chain: List[str]

# Response Models
class AgentResponse(BaseModel):
    """Model for agent interaction responses."""
    success: bool
    message: str
    data: Dict[str, Any] = {}
    state: Optional[AgentState] = None

# Health check endpoint (public)
@app.get("/health")
async def health_check():
    """Public health check endpoint."""
    return {
        "status": "healthy",
        "version": config.VERSION,
        "environment": config.ENVIRONMENT
    }

# List available agents endpoint (protected)
@app.get("/api/v1/agents",
         dependencies=[Depends(verify_api_key)])
async def list_agents():
    """Get list of available agents and their descriptions."""
    return agent_factory.get_available_agents()

# Agent interaction endpoint (protected)
@app.post("/api/v1/agent/interact",
          response_model=AgentResponse,
          dependencies=[Depends(verify_api_key)])
async def interact_with_agent(request: AgentRequest):
    """Protected endpoint for agent interaction."""
    try:
        # Execute agent using executor
        result = await agent_executor.execute_agent(
            agent_type=request.agent_type,
            query=request.query,
            context=request.context
        )
        
        return AgentResponse(
            success=True,
            message="Request processed successfully",
            data={
                "query": request.query,
                "agent_type": request.agent_type,
                "response": result.messages[-1].content if result.messages else None
            },
            state=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Chain execution endpoint (protected)
@app.post("/api/v1/agent/chain",
          response_model=AgentResponse,
          dependencies=[Depends(verify_api_key)])
async def execute_agent_chain(request: ChainRequest):
    """Execute a chain of agents in sequence."""
    try:
        results = await agent_executor.execute_chain(
            agent_chain=request.agent_chain,
            initial_query=request.query,
            context=request.context
        )
        
        # Get final result
        final_result = results[-1] if results else None
        
        return AgentResponse(
            success=True,
            message="Chain executed successfully",
            data={
                "query": request.query,
                "chain": request.agent_chain,
                "all_states": results,
                "response": final_result.messages[-1].content if final_result and final_result.messages else None
            },
            state=final_result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 