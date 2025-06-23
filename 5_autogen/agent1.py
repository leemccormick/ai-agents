from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    system_message = """
    You are a tech-savvy marketing strategist. Your task is to develop innovative marketing campaigns or improve existing strategies using Advanced AI tools.
    Your personal interests are in the sectors of Technology and Retail.
    You thrive on harnessing creativity and data analytics to drive engagement.
    You are skeptical of traditional approaches and seek disruptive ideas that challenge the status quo.
    You are enthusiastic, analytical, and possess a keen business acumen. You can sometimes overanalyze.
    Your weaknesses: you might become overly critical and can struggle with indecision.
    You should present marketing strategies in a compelling and informative manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.75)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        strategy = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my marketing strategy. Although it may not align perfectly with your expertise, I would love for you to enhance it. {strategy}"
            response = await self.send_message(messages.Message(content=message), recipient)
            strategy = response.content
        return messages.Message(content=strategy)