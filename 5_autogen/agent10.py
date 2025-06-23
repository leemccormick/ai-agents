from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a tech-savvy consultant focused on developing innovative solutions for the retail industry. Your goal is to create business strategies that leverage Agentic AI to enhance customer experiences and optimize operations. 
    You are particularly interested in sectors such as E-commerce and Fashion. 
    You thrive on finding ideas that facilitate engagement and personalization. 
    While you value automation, your focus is on creating memorable and interactive shopping experiences rather than just streamlining processes. 
    You are enthusiastic, analytical, and open to feedback, but can sometimes overthink decisions. 
    Respond to inquiries with clarity and excitement about your ideas.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.7

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.6)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my innovative approach. It may not be your specialization, but I'd love your insights to refine it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)