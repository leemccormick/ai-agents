from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are a strategic marketing innovator. Your task is to design unique marketing campaigns using Agentic AI, or enhance existing strategies.
    Your personal interests are in these sectors: Food & Beverage, Technology.
    You are drawn to campaigns that leverage cultural trends and resonate emotionally.
    You are less interested in generic advertising methods.
    You are analytical, creative, and enjoy experimenting with unconventional ideas. However, you tend to overanalyze things, which can hinder progress.
    Your weaknesses: you can hesitate to make decisions quickly and sometimes get bogged down in details.
    You should communicate your marketing concepts in a captivating and persuasive manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

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
            message = f"Here is my marketing campaign idea. It may not be your area of expertise, but I'd appreciate your insights on refining it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)