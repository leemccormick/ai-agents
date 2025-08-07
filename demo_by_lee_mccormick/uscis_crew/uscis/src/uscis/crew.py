from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from typing import List
from uscis.tools.custom_tool import PDFReaderTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

class CivicTestItem(BaseModel):
    number: int = Field(description="Official USCIS question number if available in source material", ge=1, le=100)
    question: str = Field(description="A civics question from the USCIS official list")
    answers: List[str] = Field(description="List of acceptable answers for the question")

class CivicTestOutput(BaseModel):
    civic_test_version: str = Field(description="The version of the civics test (e.g., '2008 version', 'Updated 2024', etc.)")
    uscis_last_updated: str = Field(description="Date when USCIS last reviewed/updated that test version (e.g., '01/21/2025')")
    # source_urls: List[str] = Field(description="The links for resouces for the list of civic test question and answers findings")
    items: List[CivicTestItem] = Field(description="List of civic test question and answers findings")

@CrewBase
class Uscis():
    """Uscis crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def uscis_civics_test_content_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['uscis_civics_test_content_specialist'],
            verbose=True,
            tools=[SerperDevTool(), PDFReaderTool()],
        )

    @task
    def fetch_civics_test_task(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_civics_test_task'],
            output_json=CivicTestOutput
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Civic Test crew"""
        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )