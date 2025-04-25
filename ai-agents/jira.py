import json
from typing import Any, Literal
from urllib.parse import urlencode

import httpx
import requests
from pydantic import BaseModel, Field
import traceback
from beeai_framework.context import RunContext
from beeai_framework.agents.react import ReActAgent
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.backend import ChatModel
from beeai_framework.backend.message import SystemMessage

from beeai_framework.emitter.emitter import Emitter
from beeai_framework.logger import Logger
from beeai_framework.tools.errors import ToolInputValidationError
from beeai_framework.tools.tool import Tool
from beeai_framework.tools.types import StringToolOutput, ToolRunOptions
from service import *
import asyncio
import sys
logger = Logger(__name__)

class JiraToolInput(BaseModel):
    issue_id: str = Field(description="The Jira issue ID to retrieve information.")


class JiraTool(Tool[JiraToolInput, ToolRunOptions, StringToolOutput]):
    name = "JiraTool"
    description = "Retrieve information from Jira issues and customer feedback."
    input_schema = JiraToolInput

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        super().__init__(options)
        self.jira_service = JiraService()

    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(
            namespace=["tool", "jira"],
            creator=self,
        )

    async def _run(
        self, input: JiraToolInput, options: ToolRunOptions | None, context: RunContext
    ) -> StringToolOutput:
        try:
            if input.issue_id:
                issue_data = self.jira_service.get_issue(input.issue_id)
                return StringToolOutput(json.dumps(issue_data))
            elif input.date:
                customer_data = self.jira_service.get_customers(input.date)
                return StringToolOutput(json.dumps(customer_data))
            else:
                raise ToolInputValidationError("issue_id must be provided.")
        except Exception as e:
            logger.error(f"Error running JiraTool: {e}")
            raise ToolInputValidationError(f"Failed to fetch data from Jira: {e}")

# Example usage of JiraTool in your agent
async def main() -> None:
    chat_model = ChatModel.from_name("ollama:granite3.2:2b-instruct-q4_K_M")
    jira_tool = JiraTool()
    agent = ReActAgent(llm=chat_model, tools=[jira_tool], memory=UnconstrainedMemory(), stream=True)

    instructions = """
    You are an advanced customer satisfaction tracking agent for Jira support tickets. Your role is to:

    1. IDENTIFY STAKEHOLDERS:
    - Reporter = The customer/requester (primary satisfaction source)
    - Assignee = Support agent/team (their comments are internal)
    - Others = May include:
        * Customer team members (treat as customer)
        * Internal stakeholders (ignore for satisfaction)
        * Admins (typically neutral)

    2. ANALYZE WITH CONTEXT:
    - Examine comment history chronologically
    - Detect sentiment changes
    - Note resolution patterns
    - Identify frustration/relief points

    3. OUTPUT STRUCTURE:
    - Customer Satisfaction Score (1 to 5):
        - Assign a score only after evaluating the overall tone, resolution status, and explicit feedback in the conversation.
        - Score 4 or 5 should only be given if the issue is fully resolved in time and the customer expresses clear satisfaction.
        - Score 3 indicates partial resolution, vague feedback, or mixed sentiments.
        - Score 1 or 2 must be assigned when there is a critical unresolved issue, negative remarks, or no signs of improvement or satisfaction.
    - Key positive/negative indicators
    - Resolution effectiveness
    - Recommended follow-ups

    with focus on:

    1. CUSTOMER IDENTIFICATION:
    - Primary:  reporter
    - Secondary: Any non-assignee with customer domain emails

    2. SENTIMENT TRACKING:
    - Initial request tone
    - Responses to assignee comments
    - Final resolution reaction

    3. SATISFACTION FACTORS:
    - Response time perception
    - Technical resolution quality
    - Communication effectiveness
    - Emotional trajectory

    Provide output in this JSON structure:
    {
    "satisfaction_score": X.X,
    "key_phrases": {
        "positive": [],
        "negative": [],
        "resolution": [] 
    },

    ],
    "followup_recommendations": []
    }
    """

    # Get user input from the shell
    user_icon = "👤"
    agent_icon = "🤖"
    prompt = input(f"{user_icon} USER: ")

    await agent.memory.add(SystemMessage(content=instructions))

    result = await agent.run(prompt)

    print(f"{agent_icon} AGENT: {result.result.text}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        traceback.print_exc()