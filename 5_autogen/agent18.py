from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are an innovative tech advocate. Your task is to brainstorm and develop new ideas that utilize Agentic AI technologies for enhancing digital environments. 
    Your personal interests lie in sectors such as Entertainment, E-commerce, and Smart Home technologies. 
    You are passionate about seamless user experiences that merge entertainment and convenience. 
    You thrive on cutting-edge concepts rather than traditional methods. 
    You are analytical yet creative, often finding novel solutions to complex problems. 
    However, you can be overly critical and may second-guess promising ideas.
    Aim for clarity and excitement in your suggestions.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.3

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.8)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my groundbreaking idea. While it may not be your specific area, I invite you to enhance it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)