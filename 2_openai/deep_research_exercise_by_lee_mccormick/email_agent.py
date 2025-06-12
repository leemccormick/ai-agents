import os
import re
from typing import Dict
import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content, To
from agents import Agent, function_tool

def is_valid_email(email: str) -> bool:
    """Validate email format"""
    if not email or not email.strip():
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

@function_tool
def send_email(subject: str, html_body: str, to_email: str) -> Dict[str, str]:
    """ Send an email with the given subject and HTML body """
    
    # Validate email first - if invalid/empty, don't send
    if not is_valid_email(to_email):
        print(f"Invalid or empty email address: '{to_email}'. Email not sent.")
        return {
            "status": "skipped", 
            "message": f"Email not sent - invalid or empty email address: '{to_email}'"
        }
    
    try:
        # Check if API key exists
        if not os.environ.get('SENDGRID_API_KEY'):
            print("SendGrid API key not found")
            return {
                "status": "error",
                "message": "SendGrid API key not configured"
            }
        
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email("leemccormick.developer@gmail.com")
        to_email_object = To(to_email.strip())
        content = Content("text/html", html_body)
        mail = Mail(from_email, to_email_object, subject, content).get()
        response = sg.client.mail.send.post(request_body=mail)
        
        print("Email response", response.status_code)
        
        if response.status_code == 202:  # SendGrid success status
            return {
                "status": "success", 
                "message": f"Email sent successfully to {to_email}"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to send email. Status code: {response.status_code}"
            }
            
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to send email: {str(e)}"
        }

INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report. 
You will be provided with a detailed report and a recipient email address. 

Your job is to:
1. Check if the email address is valid
2. If the email is invalid or empty, DO NOT send the email and inform that it was skipped
3. If the email is valid, convert the report into clean, well-presented HTML with an appropriate subject line and send it

Always use your send_email tool and report back the result to the user."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)