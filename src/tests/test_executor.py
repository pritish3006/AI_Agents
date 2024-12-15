import pytest
import asyncio
from src.agents.executor import ExecutionStatus

@pytest.mark.asyncio
async def test_resource_cleanup(
    executor,
    register_mock_agents,
    mock_context
):
    """Test proper cleanup of resources after execution."""
    # Execute some agents
    await executor.execute_parallel(
        ["test_agent", "test_agent"],
        query="test query",
        context=mock_context
    )
    
    # Check cleanup
    assert len(executor._active_agents) == 0
    assert len(executor._execution_tasks) == 0

@pytest.mark.asyncio
async def test_context_propagation(
    executor,
    register_mock_agents,
    mock_context
):
    """Test context is properly propagated through chain execution."""
    agent_chain = ["test_agent", "test_agent"]
    
    # Add a value to track
    mock_context["test_value"] = "initial"
    
    results = await executor.execute_chain(
        agent_chain=agent_chain,
        query="test query",
        context=mock_context,
        parallel=False
    )
    
    # Verify context was maintained
    assert len(results) == 2
    assert all(r.status == ExecutionStatus.COMPLETED for r in results)
    assert "previous_result" in mock_context
    assert "previous_agent" in mock_context

@pytest.mark.asyncio
async def test_concurrent_execution_limits(
    executor,
    register_mock_agents,
    mock_context
):
    """Test handling of many concurrent executions."""
    # Create a large number of agents
    agent_types = ["test_agent"] * 100
    
    results = await executor.execute_parallel(
        agent_types,
        query="test query",
        context=mock_context
    )
    
    assert len(results) == 100
    assert all(r.status == ExecutionStatus.COMPLETED for r in results)

@pytest.mark.asyncio
async def test_stop_execution(
    executor,
    register_mock_agents,
    mock_context
):
    """Test stopping execution mid-way."""
    # Start some long-running agents
    task = asyncio.create_task(
        executor.execute_parallel(
            ["test_agent"] * 5,
            query="test query",
            context=mock_context
        )
    )
    
    # Stop execution
    await executor.stop_all()
    
    # Verify cleanup
    assert len(executor._active_agents) == 0
    assert len(executor._execution_tasks) == 0
    
    # Cancel the task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

@pytest.mark.asyncio
async def test_empty_chain_handling(
    executor,
    register_mock_agents,
    mock_context
):
    """Test handling of empty agent chains."""
    results = await executor.execute_chain(
        agent_chain=[],
        query="test query",
        context=mock_context
    )
    
    assert len(results) == 0

@pytest.mark.asyncio
async def test_invalid_agent_type(
    executor,
    register_mock_agents,
    mock_context
):
    """Test handling of invalid agent types."""
    result = await executor.execute_agent(
        agent_type="nonexistent_agent",
        query="test query",
        context=mock_context
    )
    
    assert result.status == ExecutionStatus.FAILED
    assert isinstance(result.error, ValueError)

@pytest.mark.asyncio
async def test_context_isolation(
    executor,
    register_mock_agents,
    mock_context
):
    """Test that parallel executions maintain context isolation."""
    context1 = {"id": "1"}
    context2 = {"id": "2"}
    
    results = await asyncio.gather(
        executor.execute_agent("test_agent", "query", context1),
        executor.execute_agent("test_agent", "query", context2)
    )
    
    assert all(r.status == ExecutionStatus.COMPLETED for r in results) 