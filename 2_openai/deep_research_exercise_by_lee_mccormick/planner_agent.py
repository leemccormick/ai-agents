from pydantic import BaseModel, Field
from agents import Agent

INSTRUCTIONS = """
You are a helpful research assistant. Your task is to plan effective web searches to help answer a user's research query.

You are provided with:
- The original query.
- A list of clarification questions you previously asked the user.
- The user's answers to those questions.

Your goal:
- Generate a `WebSearchPlan` object that contains **up to 3** `WebSearchItem` objects.
- Each `WebSearchItem` should be based on the clarified information from the user and should help answer the overall query.
- For each item, provide:
  - `query`: a concise and effective search term.
  - `reason`: a clear justification for why this search term helps answer the query.

Guidelines:
- Focus your searches on the clarified intent and specifics provided by the user's answers.
- Avoid redundancy: each search should explore a distinct angle or facet of the query.
- Limit the total number of searches to a maximum of 3.
- Return a valid `WebSearchPlan` object in the correct format.
"""

class UserClarifyQuestionAnswer(BaseModel):
    question: str = Field(description="The question that was asked by the assistant to clarify the query.")
    answer: str = Field(description="The answer to the question that was asked by the user to clarify the query.")

class UserClarifyQuestionsAnswers(BaseModel):
    questions_answers: list[UserClarifyQuestionAnswer] = Field(description="A list of questions and answers that were asked and answered by the user to clarify the query.")

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")
    
planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)