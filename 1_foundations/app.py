from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr


load_dotenv(override=True)

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )

def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]

class Me:

    def __init__(self):
        self.openai = OpenAI()
        self.name = "Lee McCormick"
        reader = PdfReader("me/linkedin.pdf")
        ibm_resume_reader = PdfReader("me/ibm_resume.pdf")
        self.linkedin = ""
        self.ibm_resume = ""

        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text

        for page in ibm_resume_reader.pages:
            text = page.extract_text()
            if text:
                self.ibm_resume += text

        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()


    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n## IBM Resume:\n{self.ibm_resume}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
    

if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(me.chat, type="messages").launch()

""" 
📝 NOTE: Personal Assistant Bot - Setup and Running Instructions
Author: Lee McCormick
Description: A Gradio-based chatbot that represents Lee on his website with quality control

SETUP INSTRUCTIONS:
1. Environment Setup:
   - Create a .env file in the root directory with the following variables:
     OPENAI_API_KEY=your_openai_api_key
     GOOGLE_API_KEY=your_google_api_key
     PUSHOVER_USER=your_pushover_user_token
     PUSHOVER_TOKEN=your_pushover_app_token

2. Required Directory Structure:
   project_root/
   ├── app.py
   ├── .env
   └── me/
       ├── linkedin.pdf        # Your LinkedIn profile PDF
       ├── ibm_resume.pdf     # Your resume PDF
       ├── ccc_transcript.pdf # Your transcript PDF
       └── summary.txt        # A text file containing your professional summary

3. Install Dependencies:
   pip install python-dotenv openai requests pypdf gradio pydantic

4. Running the Application:
   Method 1 (Direct Python):
   python app.py

   Method 2 (Using uvicorn):
   uvicorn app:interface --reload

   Method 3 (With virtual environment):
   source .venv/bin/activate
   python app.py

USAGE NOTES:
- The application will start a local server (typically at http://127.0.0.1:7860)
- Open the URL in your web browser to interact with the chat interface
- The bot uses both OpenAI and Google's Gemini API for different functions
- Pushover integration is used for notifications of user interactions
- Quality control is implemented using Gemini for response evaluation

TROUBLESHOOTING:
- Ensure all API keys are valid and properly set in .env
- Check that all required PDF files are readable and properly formatted
- Verify that the 'me' directory contains all required files
- Monitor the console output for any error messages

For more information or support:
- GitHub: github.com/leemccormick
- Email: leemccormick.developer@gmail.com
"""