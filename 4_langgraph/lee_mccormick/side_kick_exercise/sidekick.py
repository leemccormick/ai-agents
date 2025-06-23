from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Any, Dict
from sidekick_tools import search_tools, write_tools, report_tools, playwright_tools
import uuid
import asyncio
from datetime import datetime
from PIL import Image
from io import BytesIO
from sidekick_models import PresenterOutput, State, EvaluatorOutput, PlanerOutput, PlanWorkFlow
from sidekick_prompts import get_planer_prompt, get_researcher_prompt, get_evaluator_system_prompt, get_evaluator_user_prompt, get_presentor_system_prompt, get_reporter_system_prompt, get_writer_system_prompt
load_dotenv(override=True)

class Sidekick:
    def __init__(self):
        self.researcher_llm_with_tools = None
        self.writter_llm_with_tools = None
        self.reporter_llm_with_tools = None
        self.planner_llm_with_output = None
        self.evaluator_llm_with_output = None
        self.presentor_llm_with_output = None
        self.manager_llm = None

        self.search_tools = None
        self.write_tools = None
        self.report_tools = None

        self.graph = None
        self.sidekick_id = str(uuid.uuid4())
        self.memory = MemorySaver()
        self.browser = None
        self.playwright = None

    async def setup(self):
        self.search_tools, self.browser, self.playwright = await playwright_tools()
        self.search_tools += await search_tools()
        self.write_tools = await write_tools()
        self.report_tools = await report_tools()

        researcher_llm = ChatOpenAI(model="gpt-4o-mini")
        self.researcher_llm_with_tools = researcher_llm.bind_tools(self.search_tools)

        reporter_llm = ChatOpenAI(model="gpt-4o-mini")
        self.reporter_llm_with_tools = reporter_llm.bind_tools(self.report_tools)

        writter_llm = ChatOpenAI(model="gpt-4o-mini")
        self.writter_llm_with_tools = writter_llm.bind_tools(self.write_tools)

        planer_llm = ChatOpenAI(model="gpt-4o-mini")
        self.planner_llm_with_output = planer_llm.with_structured_output(PlanerOutput)

        evaluator_llm = ChatOpenAI(model="gpt-4o-mini")
        self.evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)

        presentor_llm = ChatOpenAI(model="gpt-4o-mini")
        self.presentor_llm_with_output = presentor_llm.with_structured_output(PresenterOutput)

        await self.build_graph()

    async def build_graph(self):
        # Set up Graph Builder with State
        graph_builder = StateGraph(State)

        # Add nodes
        graph_builder.add_node("planer_agent", self.planer_agent)
        graph_builder.add_node("researcher_agent", self.researcher_agent)
        graph_builder.add_node("reporter_agent", self.report_agent)
        graph_builder.add_node("writer_agent", self.writer_agent)
        graph_builder.add_node("evaluator_agent", self.evaluator_agent)
        graph_builder.add_node("presentor_agent", self.presentor_agent)

        graph_builder.add_node("search_tools", ToolNode(tools=self.search_tools))
        graph_builder.add_node("report_tools", ToolNode(tools=self.report_tools))
        graph_builder.add_node("write_tools", ToolNode(tools=self.write_tools))

        # Add edges
        graph_builder.add_edge(START, "planer_agent")
        graph_builder.add_conditional_edges(
            "planer_agent", 
            self.planer_router, 
            {
                "researcher_agent": "researcher_agent",
                "reporter_agent": "reporter_agent", 
                "writer_agent": "writer_agent",
                "presentor_agent": "presentor_agent",
                "END": END
            }
        )
        graph_builder.add_conditional_edges("researcher_agent", self.research_router, {"search_tools": "search_tools", "evaluator_agent": "evaluator_agent"})
        graph_builder.add_conditional_edges("evaluator_agent", self.evaluator_route, {"researcher_agent": "researcher_agent", "planer_agent": "planer_agent"})
        graph_builder.add_conditional_edges("reporter_agent", self.report_router, {"report_tools": "report_tools", "planer_agent": "planer_agent"})
        graph_builder.add_conditional_edges("writer_agent", self.write_router, {"write_tools": "write_tools" ,"planer_agent": "planer_agent"})
        graph_builder.add_edge("search_tools", "researcher_agent")
        graph_builder.add_edge("report_tools", "reporter_agent")
        graph_builder.add_edge("write_tools", "writer_agent")
        graph_builder.add_edge("presentor_agent", "planer_agent")

        # Compile the graph
        self.graph = graph_builder.compile(checkpointer=self.memory)

    async def display_graph(self):
        png_bytes = self.graph.get_graph().draw_mermaid_png()

        if not png_bytes:
            raise ValueError("Graph rendering failed. No PNG data was returned.")

        try:
            image = Image.open(BytesIO(png_bytes))
            return image
        except Exception as e:
            raise RuntimeError(f"Could not create image from graph PNG: {str(e)}")
        
    # Nodes
    def planer_agent(self, state: State) -> Dict[str, Any]:
        system_message = get_planer_prompt(state)
        print("🤖 planer_agent() : state", state)

        # Attach system message
        found_system_message = False
        messages = state["messages"]
        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = system_message
                found_system_message = True

        if not found_system_message:
            messages = [SystemMessage(content=system_message)] + messages

        # Invoke planner LLM with structured output
        planer_result = self.planner_llm_with_output.invoke(messages)

        # Initialize active_step_index to first unfinished step (if any)
        active_step_index = 0
        for idx, step in enumerate(planer_result.plan_workflow):
            if not step.did_task_finished:
                active_step_index = idx
                break

        new_state = {
            "messages": [
                {"role": "assistant", "content": f"Generated plan:\n{planer_result.plan}"}
            ],
            "active_step_index": active_step_index,
            "plan_workflow": planer_result.plan_workflow,
            "user_input_needed": planer_result.user_input_needed,
            "success_criteria_met": planer_result.success_criteria_met
        }

        print("🤖 planer_agent() : new_state", new_state)
        return new_state

    def researcher_agent(self, state: State) -> Dict[str, Any]:
        system_message = get_researcher_prompt(state)

        messages = list(state["messages"])  # make a copy to avoid modifying the original
        found_system_message = False

        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = system_message
                found_system_message = True

        if not found_system_message:
            messages.insert(0, SystemMessage(content=system_message))

        # Invoke the LLM with tools
        response = self.researcher_llm_with_tools.invoke(messages)
        print("🤖 researcher_agent() : response", response)
        return {
            "messages": [response],
        }

    def evaluator_agent(self, state: State) -> State:
        system_message = get_evaluator_system_prompt(state)
        user_message = get_evaluator_user_prompt(state)

        evaluator_messages = [SystemMessage(content=system_message), HumanMessage(content=user_message)]

        eval_result = self.evaluator_llm_with_output.invoke(evaluator_messages)

        # Update current step status if success criteria met
        active_idx = state["active_step_index"]
        plan_workflow = state["plan_workflow"]

        if eval_result.success_criteria_met:
            plan_workflow[active_idx].did_task_finished = True

        # Update global success_criteria_met if all steps done
        all_done = all(step.did_task_finished for step in plan_workflow)

        new_state = {
            "messages": [{"role": "assistant", "content": f"Evaluator Feedback on this answer: {eval_result.feedback}"}],
            "feedback_on_work": eval_result.feedback,
            "success_criteria_met": all_done,
            "user_input_needed": eval_result.user_input_needed,
            "plan_workflow": plan_workflow,  # update workflow with new statuses
        }

        print("🤖 evaluator_agent() : new_state", new_state)
        return new_state

    def presentor_agent(self, state: State) -> State:
        system_message = get_presentor_system_prompt()
        active_step = state["plan_workflow"][state["active_step_index"]]
        user_message = f"""
        **Task:** {active_step.task}
        **Instructions:** {active_step.description}
        **Criteria:** {active_step.success_criteria}
        """

        presentor_messages = [SystemMessage(content=system_message), HumanMessage(content=user_message)]

        presentor_result = self.presentor_llm_with_output.invoke(presentor_messages)
        new_state = {
            "messages": [{"role": "assistant", "content": f"Presentation Content description: {presentor_result.description}"}],
            "presentation_content": presentor_result,
        }
        return new_state

    def report_agent(self, state: State) -> Dict[str, Any]:
        # Get system and user messages
        system_message = get_reporter_system_prompt(state)

        # Invoke the reporter LLM with tools
        response = self.reporter_llm_with_tools.invoke(system_message)

        return {
            "messages": [response],
        }

    def writer_agent(self, state: State) -> Dict[str, Any]:
        system_message = get_writer_system_prompt(state)
        # Invoke the LLM with tools
        response = self.writter_llm_with_tools.invoke(system_message)

        # Return updated state
        return {
            "messages": [response],
        }

    # Edges
    def planer_router(self, state: State) -> str:
        if state["success_criteria_met"] or state["user_input_needed"]:
            return "END"

        # Move to next unfinished step
        for i, step in enumerate(state["plan_workflow"]):
            if not step.did_task_finished:
                state["active_step_index"] = i
                return step.worker_agent_name

        # All steps done
        return "END"


    def research_router(self, state: State) -> str:
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "search_tools"
        else:
            return "evaluator_agent"


    def evaluator_route(self, state: State) -> str:
        if state["success_criteria_met"] or state["user_input_needed"]:
            return "planer_agent"
        else:
            return "researcher_agent"


    def presentor_route(self, state: State) -> str:
        # Always returns to planer_agent, you can customize if needed
        return "planer_agent"


    def report_router(self, state: State) -> str:
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "report_tools"
        else:
            return "planer_agent"

    def write_router(self, state: State) -> str:
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "write_tools"
        else:
            return "planer_agent"
    
    # Helper Functions
    def cleanup(self):
        if self.browser:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.browser.close())
                if self.playwright:
                    loop.create_task(self.playwright.stop())
            except RuntimeError:
                # If no loop is running, do a direct run
                asyncio.run(self.browser.close())
                if self.playwright:
                    asyncio.run(self.playwright.stop())


    async def run_superstep(self, message, success_criteria, history):
        config = {"configurable": {"thread_id": self.sidekick_id}}

        state = {
            "messages": message,
            "success_criteria": success_criteria or "The answer should be clear and accurate",
            "feedback_on_work": None,
            "success_criteria_met": False,
            "user_input_needed": False
        }
        result = await self.graph.ainvoke(state, config=config)
        user = {"role": "user", "content": message}
        reply = {"role": "assistant", "content": result["messages"][-2].content}
        feedback = {"role": "assistant", "content": result["messages"][-1].content}
        return history + [user, reply, feedback]