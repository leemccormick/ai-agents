# from dotenv import load_dotenv
# from openai import OpenAI
# import json
# import os
# import requests
# from pypdf import PdfReader
# import gradio as gr


# load_dotenv(override=True)

# def push(text):
#     requests.post(
#         "https://api.pushover.net/1/messages.json",
#         data={
#             "token": os.getenv("PUSHOVER_TOKEN"),
#             "user": os.getenv("PUSHOVER_USER"),
#             "message": text,
#         }
#     )


# def record_user_details(email, name="Name not provided", notes="not provided"):
#     push(f"Recording {name} with email {email} and notes {notes}")
#     return {"recorded": "ok"}

# def record_unknown_question(question):
#     push(f"Recording {question}")
#     return {"recorded": "ok"}

# record_user_details_json = {
#     "name": "record_user_details",
#     "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "email": {
#                 "type": "string",
#                 "description": "The email address of this user"
#             },
#             "name": {
#                 "type": "string",
#                 "description": "The user's name, if they provided it"
#             }
#             ,
#             "notes": {
#                 "type": "string",
#                 "description": "Any additional information about the conversation that's worth recording to give context"
#             }
#         },
#         "required": ["email"],
#         "additionalProperties": False
#     }
# }

# record_unknown_question_json = {
#     "name": "record_unknown_question",
#     "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "question": {
#                 "type": "string",
#                 "description": "The question that couldn't be answered"
#             },
#         },
#         "required": ["question"],
#         "additionalProperties": False
#     }
# }

# tools = [{"type": "function", "function": record_user_details_json},
#         {"type": "function", "function": record_unknown_question_json}]


# class Me:

#     def __init__(self):
#         self.openai = OpenAI()
#         self.name = "Lee McCormick"
#         reader = PdfReader("me/linkedin.pdf")
#         ibm_resume_reader = PdfReader("me/ibm_resume.pdf")
#         self.linkedin = ""
#         self.ibm_resume = ""

#         for page in reader.pages:
#             text = page.extract_text()
#             if text:
#                 self.linkedin += text

#         for page in ibm_resume_reader.pages:
#             text = page.extract_text()
#             if text:
#                 self.ibm_resume += text

#         with open("me/summary.txt", "r", encoding="utf-8") as f:
#             self.summary = f.read()


#     def handle_tool_call(self, tool_calls):
#         results = []
#         for tool_call in tool_calls:
#             tool_name = tool_call.function.name
#             arguments = json.loads(tool_call.function.arguments)
#             print(f"Tool called: {tool_name}", flush=True)
#             tool = globals().get(tool_name)
#             result = tool(**arguments) if tool else {}
#             results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
#         return results
    
#     def system_prompt(self):
#         system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
# particularly questions related to {self.name}'s career, background, skills and experience. \
# Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
# You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
# Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
# If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
# If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

#         system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n## IBM Resume:\n{self.ibm_resume}\n\n"
#         system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
#         return system_prompt
    
#     def chat(self, message, history):
#         messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
#         done = False
#         while not done:
#             response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
#             if response.choices[0].finish_reason=="tool_calls":
#                 message = response.choices[0].message
#                 tool_calls = message.tool_calls
#                 results = self.handle_tool_call(tool_calls)
#                 messages.append(message)
#                 messages.extend(results)
#             else:
#                 done = True
#         return response.choices[0].message.content
    

# if __name__ == "__main__":
#     me = Me()
#     gr.ChatInterface(me.chat, type="messages").launch()
    

# Personal Assistant Bot by Lee McCormick
# A Gradio-based chatbot that represents Lee on his website with quality control

from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
from pydantic import BaseModel
import gradio as gr
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# Notification system
def push_notification(text: str) -> None:
    """Send push notification via Pushover"""
    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.getenv("PUSHOVER_TOKEN"),
                "user": os.getenv("PUSHOVER_USER"),
                "message": text,
            },
            timeout=10
        )
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

# Tool functions
def record_user_details(email: str, name: str = "Name not provided", notes: str = "not provided") -> Dict[str, str]:
    """Record user contact details"""
    push_notification(f"New contact: {name} ({email}) - {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question: str) -> Dict[str, str]:
    """Record questions that couldn't be answered"""
    push_notification(f"Unknown question: {question}")
    return {"recorded": "ok"}

# Tool definitions for OpenAI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "record_user_details",
            "description": "Record user contact information when they want to get in touch",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "User's email address"},
                    "name": {"type": "string", "description": "User's name if provided"},
                    "notes": {"type": "string", "description": "Additional context about the conversation"}
                },
                "required": ["email"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "record_unknown_question",
            "description": "Record questions that couldn't be answered",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The unanswered question"}
                },
                "required": ["question"]
            }
        }
    }
]

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

class PersonalAssistant:
    """AI assistant representing Lee McCormick on her website"""
    
    def __init__(self, data_dir: str = "me"):
        self.name = "Lee McCormick"
        self.data_dir = data_dir
        self.max_retries = 2
        
        # Initialize AI clients
        self._init_ai_clients()
        
        # Load personal data
        self._load_personal_data()
    
    def _init_ai_clients(self) -> None:
        """Initialize OpenAI and Gemini clients"""
        try:
            self.openai = OpenAI()
            self.gemini = OpenAI(
                api_key=os.getenv("GOOGLE_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
            raise
    
    def _load_personal_data(self) -> None:
        """Load all personal documents and data"""
        try:
            # Load PDFs
            self.linkedin = self._extract_pdf_text("linkedin.pdf")
            self.ibm_resume = self._extract_pdf_text("ibm_resume.pdf") 
            self.ccc_transcript = self._extract_pdf_text("ccc_transcript.pdf")
            
            # Load summary
            with open(f"{self.data_dir}/summary.txt", "r", encoding="utf-8") as f:
                self.summary = f.read()
                
            logger.info("✅ All personal data loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load personal data: {e}")
            raise
    
    def _extract_pdf_text(self, filename: str) -> str:
        """Extract text from PDF file"""
        filepath = f"{self.data_dir}/{filename}"
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return ""
            
        try:
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from {filename}: {e}")
            return ""
    
    def _handle_tool_calls(self, tool_calls) -> List[Dict[str, Any]]:
        """Execute tool calls and return results"""
        results = []
        for tool_call in tool_calls:
            try:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                logger.info(f"Executing tool: {tool_name}")
                
                # Get function from globals and execute
                tool_func = globals().get(tool_name)
                if tool_func:
                    result = tool_func(**arguments)
                else:
                    result = {"error": f"Tool {tool_name} not found"}
                    
                results.append({
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id
                })
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                results.append({
                    "role": "tool", 
                    "content": json.dumps({"error": str(e)}),
                    "tool_call_id": tool_call.id
                })
        return results
    
    def _get_system_prompt(self, feedback: str = None) -> str:
        """Generate system prompt with optional feedback"""
        base_prompt = f"""You are {self.name}, answering questions on your website about your career, background, and experience.

Be professional and engaging, as if talking to potential clients or employers. Use the provided documents to answer questions accurately.

If you don't know something, use record_unknown_question tool, then ask for their email to follow up.
Try to collect visitor contact information using record_user_details tool.

## Your Background:
Summary: {self.summary}

LinkedIn: {self.linkedin}

Resume: {self.ibm_resume}

Transcript: {self.ccc_transcript}

Stay in character as {self.name} and be helpful and professional."""

        if feedback:
            base_prompt += f"\n\n## Previous Response Rejected\nFeedback: {feedback}\nPlease improve your response."
            
        return base_prompt
    
    def _evaluate_response(self, reply: str, user_message: str, history: List[Dict]) -> Evaluation:
        """Evaluate response quality using Gemini"""
        try:
            evaluator_prompt = f"""Evaluate if this response is acceptable for {self.name}'s website assistant.

The assistant should be professional, engaging, and accurate based on the provided background information.

Background: {self.summary}

Conversation History: {history}
User Message: {user_message}  
Assistant Reply: {reply}

Is this response acceptable quality? Provide feedback."""

            messages = [
                {"role": "system", "content": evaluator_prompt},
                {"role": "user", "content": "Please evaluate this response."}
            ]
            
            response = self.gemini.beta.chat.completions.parse(
                model="gemini-2.0-flash",
                messages=messages,
                response_format=Evaluation
            )
            return response.choices[0].message.parsed
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            # Default to acceptable if evaluation fails
            return Evaluation(is_acceptable=True, feedback="Evaluation service unavailable")
    
    def chat(self, message: str, history: List[Dict]) -> str:
        """Main chat function with quality control"""
        messages = [{"role": "system", "content": self._get_system_prompt()}] + history + [{"role": "user", "content": message}]
        
        for attempt in range(self.max_retries + 1):
            try:
                # Generate response with potential tool calls
                while True:
                    response = self.openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        tools=TOOLS
                    )
                    
                    if response.choices[0].finish_reason == "tool_calls":
                        # Handle tool calls
                        response_message = response.choices[0].message
                        tool_results = self._handle_tool_calls(response_message.tool_calls)
                        messages.append(response_message)
                        messages.extend(tool_results)
                    else:
                        # Got final response
                        reply = response.choices[0].message.content
                        break
                
                # Evaluate response quality
                evaluation = self._evaluate_response(reply, message, history)
                
                if evaluation.is_acceptable:
                    logger.info("✅ Response approved")
                    return reply
                else:
                    logger.warning(f"❌ Response rejected (attempt {attempt + 1}): {evaluation.feedback}")
                    if attempt < self.max_retries:
                        # Retry with feedback
                        messages = [{"role": "system", "content": self._get_system_prompt(evaluation.feedback)}] + history + [{"role": "user", "content": message}]
                    else:
                        # Max retries reached, return anyway
                        logger.warning("Max retries reached, returning response")
                        return reply
                        
            except Exception as e:
                logger.error(f"Chat error (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries:
                    return "I apologize, but I'm experiencing technical difficulties. Please try again later."
        
        return reply

# Initialize and launch
if __name__ == "__main__":
    try:
        assistant = PersonalAssistant()
        interface = gr.ChatInterface(
            assistant.chat,
            type="messages",
            title=f"Chat with {assistant.name}",
            description="Ask me about my background, experience, and projects!"
        )
        interface.launch()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"Error: {e}")