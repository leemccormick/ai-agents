from dataclasses import dataclass
from autogen_core import AgentId
import glob
import os
import random

@dataclass
class Message:
    content: str


def find_recipient() -> AgentId:
    try:
        agent_files = glob.glob("agents/agent*.py")
        agent_names = [os.path.splitext(os.path.basename(file))[0] for file in agent_files]
        agent_names = [name for name in agent_names if name != "agent"]
        agent_name = random.choice(agent_names)
        print(f"Selecting agent for refinement: {agent_name}")
        return AgentId(agent_name, "default")
    except Exception as e:
        print(f"Exception finding recipient: {e}")
        return AgentId("agent1", "default")
