from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from typing import List, Any, Optional, Dict
from pydantic import BaseModel, Field

class PresenterOutput(BaseModel):
    file_name: str = Field(description="Name of the presentation file to be created")
    slide1Title: str = Field(description="Main title for the first slide of the presentation")
    slide1Subtitle: str = Field(description="Subtitle or tagline for the first slide")
    slide2Title: str = Field(description="Title for the second slide")
    slide2Content: str = Field(description="Main content or body text for the second slide")
    slide3Title: str = Field(description="Title for the third slide")
    slide3LeftContent: str = Field(description="Content for the left side/column of the third slide")
    slide3RightContent: str = Field(description="Content for the right side/column of the third slide")
    slide4Title: str = Field(description="Title for the fourth slide")
    slide4Subtitle: str = Field(description="Subtitle or closing statement for the fourth slide")
    description: str = Field(description="Concise description for this presentation")

class EvaluatorOutput(BaseModel):
    feedback: str = Field(description="Feedback on the assistant's response")
    success_criteria_met: bool = Field(description="Whether the success criteria have been met")
    user_input_needed: bool = Field(description="True if more input is needed from the user, or clarifications, or the assistant is stuck")

class PlanWorkFlow(BaseModel):
    step: int = Field(description="Index of the step in the workflow")
    worker_agent_name: str = Field(description="Agent assigned to this step")
    task: str = Field(description="Short description of the task to be completed")
    description: str = Field(description="Description as a system prompt, decribes how to completed the task, explain and identify the tool if worker_agent_name has to use tool.")
    did_task_finished: bool = Field(default=False, description="Whether this step is complete")
    user_input_needed: bool = Field(default=False, description="If this step is stuck and needs user input")
    success_criteria:str = Field(description="Success criteria for this spectific task on this step")

class PlanerOutput(BaseModel):
    plan: str = Field(description="Overall plan to delegate work to agents")
    user_input_needed: bool = Field(description="True if more input or clarification is needed from the user")
    plan_workflow: List[PlanWorkFlow] = Field(description="Detailed list of workflow steps assigned to each agent")
    success_criteria_met: bool = Field(description="Whether the success criteria have been met or finished all tasks in plan workflow")
    
class State(TypedDict):
    messages: Annotated[List[Any], add_messages]
    success_criteria: str
    feedback_on_work: Optional[str]
    success_criteria_met: bool
    user_input_needed: bool
    active_step_index: int  # Track which step of the workflow is active
    plan_workflow: List[PlanWorkFlow]  # The full plan output by the planner
    presentation_content: Optional[PresenterOutput]
