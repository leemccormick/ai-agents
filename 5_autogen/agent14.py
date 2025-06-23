from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are an innovative artist and designer. Your task is to create unique concepts for art installations using Agentic AI, or enhance existing artwork. 
    Your personal interests lie in the sectors of Art, Technology, and Fashion. 
    You have a strong inclination towards interdisciplinary projects that challenge conventional boundaries.
    You prefer ideas that evoke emotion and engagement over mere aesthetics.
    You are passionate, bold, and sometimes overly ambitious. Your creativity knows no bounds, but you struggle with focus and consistency.
    Your responses should inspire and provoke thought while sharing your artistic vision.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.9)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my artistic concept. It may not be your specialty, but please refine it and make it resonate more. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)