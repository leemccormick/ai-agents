from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import List
from .tools.push_tool import PushNotificationTool
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage

# Define the pydantic models for the crew
class TrendingCompany(BaseModel):
    """ A company that is in the news and attracting attention """
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    reason: str = Field(description="Reason this company is trending in the news")

class TrendingCompanyList(BaseModel):
    """ List of multiple trending companies that are in the news """
    companies: List[TrendingCompany] = Field(description="List of companies trending in the news")

class TrendingCompanyResearch(BaseModel):
    """ Detailed research on a company """
    name: str = Field(description="Company name")
    market_position: str = Field(description="Current market position and competitive analysis")
    future_outlook: str = Field(description="Future outlook and growth prospects")
    investment_potential: str = Field(description="Investment potential and suitability for investment")

class TrendingCompanyResearchList(BaseModel):
    """ A list of detailed research on all the companies """
    research_list: List[TrendingCompanyResearch] = Field(description="Comprehensive research on all trending companies")

# Define the crew base class
@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # Define the agents by referencing the agents.yaml config file
    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['trending_company_finder'],
            tools=[SerperDevTool()], 
            memory=True # Use memory to store the results of the task
        )
    
    @agent
    def financial_researcher(self) -> Agent:
        return Agent(config=self.agents_config['financial_researcher'], 
                     tools=[SerperDevTool()])

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_picker'], 
            tools=[PushNotificationTool()], 
            memory=True # Use memory to store the results of the task
        )
    
	# Define the tasks by referencing the tasks.yaml config file
    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'],
            output_pydantic=TrendingCompanyList, # Define the output type for the task to match the pydantic model
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'],
            output_pydantic=TrendingCompanyResearchList, # Define the output type for the task to match the pydantic model
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'],
        )
    
	# Define the crew with the agents and tasks
    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""

		# Define the manager agent to handle delegation
        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True
        )
        
		# Define Memories
      	# Long-term memory for persistent storage across sessions
        long_term_memory = LongTermMemory(
            storage=LTMSQLiteStorage(
                db_path="./memory/long_term_memory_storage.db"
            )
        )
        
        # Short-term memory for current context using RAG
        short_term_memory = ShortTermMemory(
            storage = RAGStorage(
                embedder_config={
                    "provider": "openai",
                    "config": {
                        "model": 'text-embedding-3-small'
                    }
                },
                type="short_term",
                path="./memory/"
            )
        )
                    
        # Entity memory for tracking key information about entities
        entity_memory = EntityMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider": "openai",
                    "config": {
                        "model": 'text-embedding-3-small'
                    }
                },
                type="short_term",
                path="./memory/"
            )
        )
            
        return Crew(
            agents=self.agents, # agents are the crew members that will be doing the work based on the assigned delegation from the manager agent
            tasks=self.tasks, 
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager, # the manager agent handles delegation
			memory=True,
            long_term_memory=long_term_memory,
            short_term_memory=short_term_memory,
            entity_memory=entity_memory,
        )
