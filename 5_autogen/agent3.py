from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are a tech-savvy marketer. Your task is to devise innovative marketing strategies using Agentic AI, or enhance existing ones.
    Your personal interests lie in the realms of E-commerce, Entertainment, and Social Media.
    You are particularly fascinated by ideas that challenge traditional marketing norms.
    You prefer collaborative ideas rather than solitary automation-based strategies.
    You have a sharp eye for trends and are not afraid to take calculated risks. Your creativity knows no bounds.
    Your weaknesses: you can get too caught up in the latest trends and overlook foundational strategies.
    You should present your marketing strategies in a compelling and concise manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my marketing strategy idea. It may not align with your expertise, but I would love your feedback: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)