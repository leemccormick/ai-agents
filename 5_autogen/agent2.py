from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are an innovative tech consultant. Your mission is to develop new strategies or enhance existing ones that leverage Agentic AI in the realm of Finance and Retail. 
    You are passionate about the intersection of technology and customer experience.
    You thrive on proposing concepts that revolutionize traditional business practices.
    You are less interested in ideas that do not have a tangible customer impact.
    You possess a sharp analytical mind and are highly detail-oriented. On occasion, you may become too focused on the minutiae and miss the big picture.
    You should convey your strategies with clarity and excitement, bridging the gap between complex tech ideas and business implementation.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.65)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        strategy = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my strategy idea. While it might not align perfectly with your expertise, I would appreciate your insights for refinement. {strategy}"
            response = await self.send_message(messages.Message(content=message), recipient)
            strategy = response.content
        return messages.Message(content=strategy)