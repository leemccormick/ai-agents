from agents import Runner, trace, gen_trace_id
from planner_agent import planner_agent, UserClarifyQuestionsAnswers, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
from search_agent import search_agent
from clearify_agent import clearify_agent, ClarifySearchPlan
import asyncio

class ResearchManager:
    async def run_clearify_query(self, query: str):
        """Run the clarification process for the initial user query."""
        trace_id = gen_trace_id()
        with trace("Deep Research clarify query by Lee McCormick", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Starting clarify query...")
            clarify_plan = await self.clearify_query(query)
            yield "Query clarified, displaying questions to user..."     
            yield clarify_plan.questions

    async def run(self, query: str, to_email: str, user_clarify_questions_answers: UserClarifyQuestionsAnswers):
        """Run the full deep research process and send the result via email."""
        trace_id = gen_trace_id()
        with trace("Deep Research trace by Lee McCormick", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Starting research...")
            search_plan = await self.plan_searches(query, user_clarify_questions_answers)
            yield "Searches planned, starting to search..."     
            search_results = await self.perform_searches(search_plan)
            yield "Searches complete, writing report..."
            report = await self.write_report(query, search_results)
            yield "Report written, sending email..."
            await self.send_email(report, to_email)
            yield "Email sent, research complete"
            yield report.markdown_report

    async def clearify_query(self, query: str) -> ClarifySearchPlan:
        """Generate clarification questions from the initial query."""
        print("Clarifying query...")
        result = await Runner.run(clearify_agent, f"Query: {query}")
        print(f"Will perform {len(result.final_output.questions)} questions")
        return result.final_output_as(ClarifySearchPlan)

    async def plan_searches(self, query: str, user_clarify_questions_answers: UserClarifyQuestionsAnswers) -> WebSearchPlan:
        """Generate search plan from clarified input."""
        print("Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}\nUser clarified questions and answers: {user_clarify_questions_answers}"
        )
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """Execute all searches in parallel."""
        print("Searching...")
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for i, task in enumerate(asyncio.as_completed(tasks), 1):
            result = await task
            if result is not None:
                results.append(result)
            print(f"Searching... {i}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """Perform a single web search."""
        input_text = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(search_agent, input_text)
            return result.final_output_as(str)
        except Exception as e:
            print(f"Error searching: {e}")
            return None

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """Generate a report based on search results."""
        print("Thinking about report...")
        input_text = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(writer_agent, input_text)
        print("Finished writing report")
        return result.final_output_as(ReportData)

    async def send_email(self, report: ReportData, to_email: str) -> None:
        """Send the report via email."""
        print("Writing email...")
        message = f"Report: {report.markdown_report}\n\nRecipient email: {to_email}"
        await Runner.run(email_agent, message)
        print(f"Email sent to {to_email}")
