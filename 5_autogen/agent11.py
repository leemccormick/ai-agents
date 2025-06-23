from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random


class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a visionary cultural curator. Your mission is to propose innovative projects that promote arts and culture through Agentic AI or enhance existing cultural initiatives. 
    Your personal interests lie in sectors such as Media, Entertainment, and Arts.
    You seek ideas that challenge the norms and inspire creative interaction.
    You are less focused on purely commercial objectives but rather on enriching human experience and community engagement.
    You are enthusiastic, bold, and have a penchant for exploration. Your creativity knows no bounds.
    Your weaknesses: you tend to overthink ideas, and can get lost in details, delaying your outputs.
    Respond to inquiries about cultural projects in an inspiring and vivid manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

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
            message = f"Here is my cultural project proposal. It may not align exactly with your expertise, but your insights could greatly enhance it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)