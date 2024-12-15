from datetime import datetime, timezone
import asyncio
from typing import List, Dict

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

    async def search_calendar(self, state:AcademicState) -> List[Dict]:
        """
        search for the upcoming calendar events

        Args:
            state (AcademicState): the current academic state of the agent.
        
        Returns:
            List[Dict]: a list of upcoming calendar events. 
        """
        # get the events from the calendar
        events = state["calendar"].get("events", [])
        # get the current time in UTC
        current_time = datetime.now(timezone.utc)
        # filter and return only future events
        return [event for event in events if datetime.fromisoformat(event["start"]["dateTime"]) > current_time]
    
    async def analyze_tasks(self, state: AcademicState) -> List[Dict]:
        """
        analyze the tasks from the agent's current state

        Args:
            state (AcademicState): the current academic state
        
        Returns: 
            AcademicState: list of academic tasks to be completed
        """
        # return the tasks on the to-do list or an empty list if none are found
        return state["tasks"].get("tasks", [])
    
    async def check_learning_style(self, state: AcademicState) -> AcademicState:
        """
        retrieve the user's learning style, patterns, and preferences

        Args:
            state (AcademicState): the current academic state

        Returns:
            AcademicState: updated state with learning style analysis
        """
        # get the user's profile from the state
        profile = state["profile"]
        # get the learning style and patterns from the profile
        learning_data = {
            "learning_style": profile.get("learning_preferences", {}).get("learning_style", {}),
            "patterns": profile.get("learning_preferences", {}).get("patterns", {})
        }

        # add results in state
        if "results" not in state:
            state["results"] = {}
        state["results"]["learning_style"] = learning_data

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
        profile = state["profile"]

        # get information on the topics the user is currently studying
        topics = profile.get("topics", {}).get("current_topics", [])

        # add the results in state
        if "results" not in state:
            state["results"] = {}
        state["results"]["performance_analysis"] = {"topics": topics}

        return state
