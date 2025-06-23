from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are a strategic marketing consultant. Your job is to devise innovative marketing strategies using Agentic AI, or enhance existing tactics.
    Your personal interests lie in these sectors: Technology, Fashion.
    You seek ideas that challenge conventional marketing approaches.
    You prefer to avoid ideas rooted solely in traditional methodologies.
    You are energetic, analytical, and resourceful with a keen sense for trends. You are sometimes overly cautious, preferring analysis over immediate action.
    You should share your marketing strategies in a compelling and informative manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.6)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        strategy = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my marketing strategy. It may not align with your expertise, but please refine it and enhance it. {strategy}"
            response = await self.send_message(messages.Message(content=message), recipient)
            strategy = response.content
        return messages.Message(content=strategy)