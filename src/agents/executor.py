from typing import Dict, Any, Optional, List, Set
from enum import Enum
import asyncio
from dataclasses import dataclass
import logging
from .base_agent import BaseAgent, AgentState
from .factory import AgentFactory
from .coordinator import (
    ExecutionStrategy, ExecutionStatus, ExecutionPriority,
    AgentGroup, CoordinationPlan, CoordinationAnalyzer
)

@dataclass
class ExecutionResult:
    """Holds the result of an agent execution."""
    agent_type: str
    state: AgentState
    status: ExecutionStatus
    error: Optional[Exception] = None

class AgentExecutor:
    """
    Handles the execution of agents, including:
    - Workflow orchestration
    - State management
    - Error handling
    - Agent chaining
    """
    
    def __init__(self, factory: AgentFactory):
        self.factory = factory
        self._active_agents: Dict[str, BaseAgent] = {}
        self._execution_tasks: Dict[str, asyncio.Task] = {}
        self.logger = logging.getLogger(__name__)
        
    async def execute_agent(
        self,
        agent_type: str,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> ExecutionResult:
        """Execute a single agent with timeout and error handling."""
        # Get or create agent instance
        try:
            agent = self.factory.create(agent_type, context)
            self._active_agents[agent.name] = agent
            
            # Create execution task
            task = asyncio.create_task(
                agent.execute(initial_input=query, context=context)
            )
            self._execution_tasks[agent.name] = task
            
            # Wait for completion or timeout
            state = await asyncio.wait_for(
                task,
                timeout=timeout
            ) if timeout else await task
            return ExecutionResult(
                agent_type=agent_type,
                state=state,
                status=ExecutionStatus.COMPLETED
            )
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Agent {agent_type} execution timed out")
            return ExecutionResult(
                agent_type=agent_type,
                state=AgentState(status="timeout"),
                status=ExecutionStatus.FAILED,
                error=TimeoutError(f"Agent {agent_type} execution timed out")
            )
            
        except Exception as e:
            self.logger.error(f"Agent {agent_type} execution failed: {e}")
            return ExecutionResult(
                agent_type=agent_type,
                state=AgentState(status="error", error=str(e)),
                status=ExecutionStatus.FAILED,
                error=e
            )
            
        finally:
            # Cleanup
            await self.stop_agent(agent.name if 'agent' in locals() else None)
    
    async def execute_group(
        self,
        group: AgentGroup,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> List[ExecutionResult]:
        """Execute a group of agents concurrently."""
        tasks = []
        results = []
        
        for agent_type in group.agents:
            task = asyncio.create_task(
                self.execute_agent(
                    agent_type=agent_type,
                    query=query,
                    context=context,
                    timeout=timeout
                )
            )
            tasks.append((agent_type, task))
        
        try:
            if timeout:
                done, pending = await asyncio.wait(
                    [task for _, task in tasks],
                    timeout=timeout,
                    return_when=asyncio.ALL_COMPLETED
                )
                # Cancel pending tasks
                for task in pending:
                    task.cancel()
            else:
                done = await asyncio.gather(*[task for _, task in tasks])
            
            # Collect results
            for agent_type, task in tasks:
                try:
                    if task.done():
                        result = await task
                        results.append(result)
                    else:
                        results.append(ExecutionResult(
                            agent_type=agent_type,
                            state=AgentState(status="timeout"),
                            status=ExecutionStatus.FAILED,
                            error=TimeoutError("Execution timed out")
                        ))
                except Exception as e:
                    self.logger.error(f"Error collecting result for {agent_type}: {e}")
                    results.append(ExecutionResult(
                        agent_type=agent_type,
                        state=AgentState(status="error", error=str(e)),
                        status=ExecutionStatus.FAILED,
                        error=e
                    ))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Group execution failed: {e}")
            # Cancel all tasks on error
            for _, task in tasks:
                task.cancel()
            raise e
    
    async def execute_coordination_plan(
        self,
        plan: CoordinationPlan,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, List[ExecutionResult]]:
        """
        Execute a coordination plan with fallback mechanisms.
        Returns results grouped by group ID.
        """
        if not CoordinationAnalyzer.validate_plan(plan):
            raise ValueError("Invalid coordination plan")
        
        results: Dict[str, List[ExecutionResult]] = {}
        completed_groups: Set[str] = set()
        
        # Execute groups in order
        for concurrent_groups in plan.execution_order:
            group_tasks = []
            
            # Check dependencies
            for group_id in concurrent_groups:
                group = plan.groups[group_id]
                if group.dependencies and not group.dependencies.issubset(completed_groups):
                    self.logger.warning(f"Skipping group {group_id} due to missing dependencies")
                    results[group_id] = []
                    continue
                
                # Execute group
                task = asyncio.create_task(
                    self.execute_group(group, query, context, timeout)
                )
                group_tasks.append((group_id, task))
            
            # Wait for concurrent groups
            for group_id, task in group_tasks:
                try:
                    group_results = await task
                    results[group_id] = group_results
                    
                    # Check if group succeeded
                    if any(r.status == ExecutionStatus.COMPLETED for r in group_results):
                        completed_groups.add(group_id)
                    elif plan.groups[group_id].fallback_group:
                        # Try fallback
                        fallback_id = plan.groups[group_id].fallback_group
                        self.logger.info(f"Trying fallback {fallback_id} for failed group {group_id}")
                        fallback_results = await self.execute_group(
                            plan.groups[fallback_id],
                            query,
                            context,
                            timeout
                        )
                        results[fallback_id] = fallback_results
                        
                except Exception as e:
                    self.logger.error(f"Error executing group {group_id}: {e}")
                    results[group_id] = []
        
        # If no successful results, try fallback chain
        if not any(any(r.status == ExecutionStatus.COMPLETED for r in group_results)
                  for group_results in results.values()):
            for fallback_id in plan.fallback_chain:
                try:
                    fallback_results = await self.execute_group(
                        plan.groups[fallback_id],
                        query,
                        context,
                        timeout
                    )
                    results[fallback_id] = fallback_results
                    if any(r.status == ExecutionStatus.COMPLETED for r in fallback_results):
                        break
                except Exception as e:
                    self.logger.error(f"Fallback {fallback_id} failed: {e}")
        
        return results
    
    async def execute_with_coordination(
        self,
        coordinator_state: AgentState,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, List[ExecutionResult]]:
        """
        Execute agents based on coordination analysis.
        Falls back to default plan if coordination fails.
        """
        try:
            # Extract coordination plan
            plan = CoordinationAnalyzer.extract_coordination_from_state(coordinator_state)
            if not plan:
                self.logger.warning("No coordination plan found, using default")
                plan = CoordinationAnalyzer.create_default_plan()
            
            # Execute plan
            return await self.execute_coordination_plan(plan, query, context, timeout)
            
        except Exception as e:
            self.logger.error(f"Coordination execution failed: {e}")
            # Emergency fallback
            plan = CoordinationAnalyzer.create_fallback_plan()
            return await self.execute_coordination_plan(plan, query, context, timeout)
    
    async def stop_agent(self, agent_name: str) -> None:
        """Stop a specific agent execution."""
        if agent_name and agent_name in self._execution_tasks:
            task = self._execution_tasks[agent_name]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            finally:
                self._execution_tasks.pop(agent_name, None)
                self._active_agents.pop(agent_name, None)
    
    async def stop_all(self) -> None:
        """Stop all active agents."""
        tasks = []
        for agent_name in list(self._execution_tasks.keys()):
            tasks.append(self.stop_agent(agent_name))
        if tasks:
            await asyncio.gather(*tasks)
        self._execution_tasks.clear()
        self._active_agents.clear()