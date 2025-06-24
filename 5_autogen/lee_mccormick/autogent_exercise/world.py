from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntimeHost
from agent import Agent
from creator import Creator
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntime
from autogen_core import AgentId
import messages
import asyncio
import os
import sys

HOW_MANY_AGENTS = 5

async def create_and_message(worker, creator_id, i: int):
    try:
        result = await worker.send_message(messages.Message(content=f"agent{i}.py"), creator_id)

        # Construct full path for the idea file
        idea_dir = "ideas"
        os.makedirs(idea_dir, exist_ok=True)

        idea_path = os.path.join(idea_dir, f"idea{i}.md")

        # Save the idea content to the ideas/ directory
        with open(idea_path, "w", encoding="utf-8") as f:
            f.write(result.content)

    except Exception as e:
        print(f"Failed to run worker {i} due to exception: {e}")

async def main():
    host = GrpcWorkerAgentRuntimeHost(address="localhost:50051")
    host.start() 
    worker = GrpcWorkerAgentRuntime(host_address="localhost:50051")
    await worker.start()
    result = await Creator.register(worker, "Creator", lambda: Creator("Creator"))
    creator_id = AgentId("Creator", "default")

    # 1. Create agents/ folder if it doesn't exist
    agent_dir = "agents"
    os.makedirs(agent_dir, exist_ok=True)

    # Ensure agents/ is a package
    init_path = os.path.join(agent_dir, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as f:
            pass  # create empty __init__.py

    # Optionally, ensure the parent directory is in sys.path
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())

    coroutines = [create_and_message(worker, creator_id, i) for i in range(1, HOW_MANY_AGENTS+1)]
    await asyncio.gather(*coroutines)
    try:
        await worker.stop()
        await host.stop()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    asyncio.run(main())


