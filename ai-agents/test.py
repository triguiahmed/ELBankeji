import asyncio
import sys
import traceback
from beeai_framework.agents.react import ReActAgent
from beeai_framework.backend import ChatModel
from beeai_framework.errors import FrameworkError
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.backend.message import SystemMessage

# Import the JiraTool
from service import JiraTool  # Adjust the import based on your file structure

async def main() -> None:
    chat_model = ChatModel.from_name("ollama:granite3.2:2b-instruct-q4_K_M")
    
    # Initialize the JiraTool
    jira_tool = JiraTool()

    agent = ReActAgent(llm=chat_model, tools=[jira_tool], memory=UnconstrainedMemory())
    
    import time
    local_time = time.localtime()
    date = time.strftime("%Y-%m-%d", local_time)
    time_now = time.strftime("%H:%M", local_time)
    
    instructions = """
    You are an agent named Quark. Your job is to track customer feedback from support tickets in Jira.
    """
    prompt = "Track customer feedback from support tickets in Jira JIRA-6845. "

    await agent.memory.add(SystemMessage(content=instructions))

    result = await agent.run(prompt)

    print("answer:", result.result.text)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except FrameworkError as e:
        traceback.print_exc()
        sys.exit(e.explain())