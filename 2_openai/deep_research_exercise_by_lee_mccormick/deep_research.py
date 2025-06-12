import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager
from clearify_agent import ClarifyItem
from planner_agent import UserClarifyQuestionsAnswers, UserClarifyQuestionAnswer

load_dotenv(override=True)

# Run the deep research 
async def run_deep_research(query: str, to_email: str, question_1: str, question_2: str, question_3: str, answer_1: str, answer_2: str, answer_3: str):
    user_clarify_questions_answers = UserClarifyQuestionsAnswers(
        questions_answers=[
            UserClarifyQuestionAnswer(question=question_1, answer=answer_1),
            UserClarifyQuestionAnswer(question=question_2, answer=answer_2),
            UserClarifyQuestionAnswer(question=question_3, answer=answer_3),
        ]
    )

    async for chunk in ResearchManager().run(query, to_email, user_clarify_questions_answers):
        yield chunk

# Ask the clarify questions to the user
async def ask_clarify_questions(query: str) -> list[ClarifyItem]:
    """Call clearify_query directly - no streaming"""
    try:
        manager = ResearchManager()
        # Call the internal method directly (no yielding)
        result = await manager.clearify_query(query)
        print("🤣 Result: ", result.questions)
        return result.questions

    except Exception as e:
        print(f"Error: {e}")
        return []
    
# UI with gradio
with gr.Blocks(theme=gr.themes.Default(primary_hue="violet")) as ui:
    gr.Markdown("# Deep Research By Lee McCormick")
    # Inputs : query
    query_textbox = gr.Textbox(label="What topic would you like to research?")

    # Placeholder textboxes for questions and answers
    question_1_label = gr.Markdown(visible=False)
    answer_1 = gr.Textbox(label="Answer 1", visible=False, interactive=True)
    question_2_label = gr.Markdown(visible=False)
    answer_2 = gr.Textbox(label="Answer 2", visible=False, interactive=True)
    question_3_label = gr.Markdown(visible=False)
    answer_3 = gr.Textbox(label="Answer 3", visible=False, interactive=True)

    # Email textbox for sending the report to
    email_label = gr.Markdown(visible=False)
    email_textbox = gr.Textbox(
        label="Email to send the report to (optional)", 
        placeholder="your.email@example.com",
        visible=False
    )

    # Buttons
    clearify_button = gr.Button("Run Deep Research", variant="primary")
    continue_button = gr.Button("Continue Research", visible=False, interactive=False, variant="primary")

    # Report
    report = gr.Markdown(label="Report")

    # UI Functions : Show the questions and answers action 
    async def show_questions(query):
        questions = await ask_clarify_questions(query)
        updates = []

        if len(questions) == 0:
            updates.extend([
                gr.update(visible=False), # question_1_label
                gr.update(visible=False), # answer_1
                gr.update(visible=False), # question_2_label
                gr.update(visible=False), # answer_2
                gr.update(visible=False), # question_3_label
                gr.update(visible=False), # answer_3
                gr.update(visible=False), # email_label
                gr.update(visible=False), # email_textbox
                gr.update(visible=True),  # clearify_button
                gr.update(visible=False), # continue_button
            ])
        else:
            # Show questions and answers dynamically
            updates.append(gr.update(value=f"**Q1:** {questions[0].question}", visible=True))
            updates.append(gr.update(visible=True, interactive=True))

            if len(questions) > 1:
                updates.append(gr.update(value=f"**Q2:** {questions[1].question}", visible=True))
                updates.append(gr.update(visible=True, interactive=True))
            else:
                updates.append(gr.update(visible=False))
                updates.append(gr.update(visible=False))

            if len(questions) > 2:
                updates.append(gr.update(value=f"**Q3:** {questions[2].question}", visible=True))
                updates.append(gr.update(visible=True, interactive=True))
            else:
                updates.append(gr.update(visible=False))
                updates.append(gr.update(visible=False))

            updates.append(gr.update(value=f"**Email**", visible=True)) # email_label visible
            updates.append(gr.update(visible=True)) # email_textbox visible
            updates.append(gr.update(visible=False)) # clearify_button invisible
            updates.append(gr.update(visible=True))  # continue_button visible

        return updates
    
    # UI Function : check all answers and disable the continue button
    def check_all_answers_filled(a1, a2, a3):
        if all(a.strip() for a in [a1, a2, a3]):
            return gr.update(visible=True, interactive=True)
        return gr.update(visible=True, interactive=False)

    # Trigger check on every answer input
    answer_1.input(fn=check_all_answers_filled, inputs=[answer_1, answer_2, answer_3], outputs=[continue_button])
    answer_2.input(fn=check_all_answers_filled, inputs=[answer_1, answer_2, answer_3], outputs=[continue_button])
    answer_3.input(fn=check_all_answers_filled, inputs=[answer_1, answer_2, answer_3], outputs=[continue_button])

    # Button Click : Clarify Button
    clearify_button.click(
        fn=show_questions,
        inputs=[query_textbox],
        outputs=[
            question_1_label,
              answer_1,
            question_2_label,
              answer_2,
            question_3_label,
              answer_3,
              email_label,
            email_textbox,
            clearify_button,
            continue_button
        ],
    )

    # Button Click : Continue button
    continue_button.click(
        fn=run_deep_research, 
        inputs=[
            query_textbox, 
            email_textbox,
            question_1_label, 
            answer_1,
            question_2_label, 
            answer_2,
            question_3_label, 
            answer_3,
          ], 
        outputs=report
    )

# Launch the UI : uv run deep_research.py
ui.launch()