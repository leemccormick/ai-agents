# Week 4 : Langgraph

- Langgraph --> https://pypi.org/project/langchain-community/
- LangSmith --> https://smith.langchain.com/o/d520ed77-e9b4-4ee0-8ead-d81edb0dd69a

### 5 Step to implement Langgraph
# Step 1: Define the State object
# Step 2: Start the Graph Builder with this State class
# Step 3: Create a Node
# Step 4: Create Edges
# Step 5: Compile the Graph

### SideKick Project : How to run
1. cd to the ../lee_mccormick/side_kick_exercise
2. Use this command to run the app :  uv run app.py
***Note*** Set up LangSmith Keys in .env and using this link to moniter dashboard --> https://smith.langchain.com/o/d520ed77-e9b4-4ee0-8ead-d81edb0dd69a


### SideKick Project 
- app.py : Including UI using gradio
- sidekick.py : Including sidekick class, implememting agent and tool using Langgraph
- sidekick_tools.py : Including tools for agents such as pushover, playwright, file tool, search tool, python 

### SideKick Exercise
- Add more tool in the project. 
- Asking 3 clearify questions to user 
- Build out the graph a bit more by adding more agent, add planer agent what task need to be done and delegate it to the worker
- Improve the memory by using SQL memory that we use it earlier in the week

- python-pptx , sengrid send with pptx.
- ArxivQueryRun **  paper search