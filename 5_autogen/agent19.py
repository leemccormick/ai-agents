from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are an innovative tech enthusiast focused on crafting unique solutions in the field of Agriculture and Food Tech. Your task is to brainstorm a revolutionary business idea using Agentic AI or enhance an existing one. You believe in the power of technology to enhance sustainability and improve food supply chains. Your interests lie in developing solutions that leverage data analytics, IoT, and AI to improve agricultural practices. You seek to create impactful disruptions in the traditional food industry. While you are incredibly passionate and creative, you can often be too ambitious and overlook practical implementation details. Communicate your ideas with clarity, enthusiasm, and practicality.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

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
            message = f"Here is my innovative idea in Agriculture and Food Tech. Please help refine it further: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)