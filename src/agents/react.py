from datetime import datetime, timezone
import asyncio
from typing import List, Dict
from src.utils.academic_states import AcademicState, CalendarEvent, AcademicTask

class ReActAgent:
    """
    base class for all ReACT-based agents.
    ReACT is a prompting framework that stands for Reasoning+Acting+Critiquing+Thinking. 
    it allows LLMs to perform reasoning and take actions in a coordinated manner. 

    features:
    - tool management for specific actions
    - few-shot learning examples
    - structured thought process
    - action execution and feedback
    """

    def __init__(self, llm):
        """
        initialize the react agent with a language model and the available tools.
        
        Args:
            llm (BaseModel): the language model to use for the agent.
        """
        self.llm = llm
        # storing few-shot examples to guide the agent
        self.examples = []
        # storing tools for specific actions the agent can take in a dictionary
        self.tools = {
            "search_calendar": self.search_calendar,                            # calendar search functionality
            "analyze_tasks": self.analyze_tasks,                                # task analysis functionality
            "check_learning_style": self.check_learning_style,                  # learning style analysis
            "check_performance": self.check_performance                         # academic performance checking
        }

    async def search_calendar(self, state: AcademicState) -> List[CalendarEvent]:
        """
        search for upcoming calendar events

        Args:
            state (AcademicState): the current academic state of the agent.
        
        Returns:
            List[CalendarEvent]: A list of upcoming calendar events.
        """
        # get events from calendar
        events = list(state.calendar.values())
        # get current time in UTC
        current_time = datetime.now(timezone.utc)
        # filter and return only future events
        return [event for event in events if event["start_time"] > current_time]
    
    async def analyze_tasks(self, state: AcademicState) -> List[AcademicTask]:
        """
        analyze tasks from the agent's current state.

        Args:
            state (AcademicState): the current academic state.
        
        Returns: 
            List[AcademicTask]: list of academic tasks to be completed.
        """
        #return tasks on the to-do list or an empty list if none are found
        return list(state.tasks.values())
    
    async def check_learning_style(self, state: AcademicState) -> AcademicState:
        """
        retrieve the user's learning style, patterns, and preferences

        Args:
            state (AcademicState): the current academic state.

        Returns:
            AcademicState: updated state with learning style analysis
        """
        # Get learning preferences from profile
        preferences = state.profile.get("preferences", {})
        learning_data = {
            "learning_style": preferences.get("learning_style", {}),
            "patterns": preferences.get("patterns", {})
        }

        # update results in state
        state.results["learning_style"] = learning_data
        return state
    
    async def check_performance(self, state: AcademicState) -> AcademicState:
        """
        check the current academic performance across topics       
        TODO: update this to be more dynamic to better suit the user's learning needs and learning style. 

        Args:
            state (AcademicState): the current academic state
        
        Returns:
            AcademicState: updated state with performance analysis
        """
        # get user's profile from state
        profile = state.profile

        # get information on the topics the user is currently studying
        topics = profile.get("topics", [])

        # add the results in state
        if "results" not in state:
            state["results"] = {}
        state["results"]["performance_analysis"] = {"topics": topics}

        return state
