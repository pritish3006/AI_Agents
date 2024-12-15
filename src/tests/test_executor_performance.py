import pytest
import asyncio
import time
from src.agents.executor import ExecutionStatus

@pytest.mark.performance
@pytest.mark.asyncio
async def test_parallel_execution_scaling(
    executor,
    register_mock_agents,
    mock_context
):
    """Test how execution time scales with number of parallel agents."""
    agent_counts = [1, 10, 50, 100]
    times = []
    
    for count in agent_counts:
        start_time = time.time()
        
        results = await executor.execute_parallel(
            ["test_agent"] * count,
            query="test query",
            context=mock_context
        )
        
        execution_time = time.time() - start_time
        times.append(execution_time)
        
        # Verify all executions succeeded
        assert len(results) == count
        assert all(r.status == ExecutionStatus.COMPLETED for r in results)
    
    # Check scaling is roughly linear
    # Time per agent should not increase significantly with count
    time_per_agent = [t/c for t, c in zip(times, agent_counts)]
    max_variation = max(time_per_agent) / min(time_per_agent)
    assert max_variation < 3  # Allow some variation but not extreme

@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_usage(
    executor,
    register_mock_agents,
    mock_context
):
    """Test memory usage during large parallel executions."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Execute large number of agents
    results = await executor.execute_parallel(
        ["test_agent"] * 500,
        query="test query",
        context=mock_context
    )
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Check memory usage
    assert len(results) == 500
    assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase
    
    # Verify cleanup
    assert len(executor._active_agents) == 0
    assert len(executor._execution_tasks) == 0

@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_chains(
    executor,
    register_mock_agents,
    mock_context
):
    """Test performance of multiple concurrent chain executions."""
    chains = [["test_agent", "test_agent"]] * 10
    
    start_time = time.time()
    
    # Execute multiple chains concurrently
    results = await asyncio.gather(*[
        executor.execute_chain(
            agent_chain=chain,
            query=f"test query {i}",
            context=mock_context.copy(),
            parallel=False
        )
        for i, chain in enumerate(chains)
    ])
    
    execution_time = time.time() - start_time
    
    # Verify results
    assert len(results) == 10
    assert all(len(chain_result) == 2 for chain_result in results)
    assert all(
        r.status == ExecutionStatus.COMPLETED
        for chain_result in results
        for r in chain_result
    )
    
    # Check execution time is reasonable
    assert execution_time < 5  # Should complete in under 5 seconds

@pytest.mark.performance
@pytest.mark.asyncio
async def test_resource_usage_under_load(
    executor,
    register_mock_agents,
    mock_context
):
    """Test resource usage under heavy load conditions."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_cpu_percent = process.cpu_percent()
    
    # Create heavy load
    tasks = []
    for _ in range(5):
        task = asyncio.create_task(
            executor.execute_parallel(
                ["test_agent"] * 100,
                query="test query",
                context=mock_context.copy()
            )
        )
        tasks.append(task)
    
    # Wait for all tasks
    results = await asyncio.gather(*tasks)
    
    final_cpu_percent = process.cpu_percent()
    cpu_increase = final_cpu_percent - initial_cpu_percent
    
    # Verify results
    assert len(results) == 5
    assert all(len(batch) == 100 for batch in results)
    
    # Check resource usage
    assert cpu_increase < 90  # CPU usage shouldn't max out
    assert len(executor._active_agents) == 0
    assert len(executor._execution_tasks) == 0 