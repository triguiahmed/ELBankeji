import asyncio
import json
import time
import traceback

from beeai_framework.backend.chat import ChatModel
from beeai_framework.context import RunContext
from beeai_framework.emitter.emitter import Emitter
from beeai_framework.logger import Logger
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.tools.tool import Tool
from beeai_framework.tools.types import StringToolOutput, ToolRunOptions
from beeai_framework.workflows.agent import AgentWorkflow, AgentWorkflowInput

from beeai_framework.tools.errors import ToolInputValidationError
from pydantic import BaseModel
from typing import Any, Literal, Optional

from newspaper import Article
from bank_service import BankAPIClient

logger = Logger(__name__)

# ---- INPUT SCHEMAS ----
class BankToolInput(BaseModel):
    action: Literal["request-loan", "make-transfer", "get-balance", "get-transaction-history"]
    user: str
    amount: Optional[float]
    receiver: Optional[str]

class ScraperToolInput(BaseModel):
    url: str

# ---- TOOLS ----
class ScraperTool(Tool[ScraperToolInput, ToolRunOptions, StringToolOutput]):
    name = "ScraperTool"
    description = "Scrapes the main content from a webpage URL."
    input_schema = ScraperToolInput

    def __init__(self, options: dict[str, any] | None = None):
        super().__init__(options)

    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(namespace=["tool", "scraper"], creator=self)

    async def _run(self, input: ScraperToolInput, options: ToolRunOptions | None, context: RunContext) -> StringToolOutput:
        try:
            article = Article(input.url)
            article.download()
            article.parse()
            result = {"title": article.title, "text": article.text}
            return StringToolOutput(json.dumps(result))
        except Exception as e:
            traceback.print_exc()
            return StringToolOutput(json.dumps({"error": f"Failed to scrape {input.url}: {str(e)}"}))

class BankTool(Tool[BankToolInput, ToolRunOptions, StringToolOutput]):
    name = "BankTool"
    description = (
        "Perform banking actions: request-loan, make-transfer, get-balance, get-transaction-history"
    )
    input_schema = BankToolInput

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        super().__init__(options)
        self.bank_client = BankAPIClient()

    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(namespace=["tool", "bank"], creator=self)

    async def _run(self, input: BankToolInput, options: ToolRunOptions | None, context: RunContext) -> StringToolOutput:
        try:
            if input.action == "request-loan":
                if input.amount is None:
                    raise ToolInputValidationError("Amount is required for loan.")
                result = self.bank_client.request_loan(input.user, input.amount)

            elif input.action == "make-transfer":
                if input.amount is None or input.receiver is None:
                    raise ToolInputValidationError("Amount and receiver are required for transfer.")
                result = self.bank_client.send_money(input.user, input.receiver, input.amount)

            elif input.action == "get-balance":
                result = self.bank_client.get_balance(input.user)

            elif input.action == "get-transaction-history":
                result = self.bank_client.get_transactions_history(input.user)

            else:
                raise ToolInputValidationError("Invalid action provided.")

            return StringToolOutput(json.dumps(result))
        except Exception as e:
            logger.error(f"Error in BankTool: {e}")
            raise ToolInputValidationError(f"Banking operation failed: {e}")
        

def create_workflow(user: str = "John Doe") -> AgentWorkflow:
    chat_model = ChatModel.from_name("ollama:granite3.2:2b-instruct-q4_K_M")
    workflow = AgentWorkflow(name="Multi-agent Smart Banking Assistant")

    local_time = time.localtime()
    date = time.strftime("%Y-%m-%d", local_time)
    time_now = time.strftime("%H:%M", local_time)

    base_context = f"""
    You are assisting user: {user}. Current date: {date}, time: {time_now}.
    You understand English, French, Arabic and Tunisian dialects.
    Respond in the language used by the user.
    """

    workflow.add_agent(
        name="BankAgent",
        role="Handles banking requests.",
        instructions=base_context + """
        Use BankTool to:
        - request-loan (amount required)
        - make-transfer (amount and receiver required)
        - get-balance
        - get-transaction-history
        """,
        tools=[BankTool()],
        llm=chat_model,
    )

    workflow.add_agent(
        name="FAQScraper",
        role="Scrapes bank FAQs to answer queries.",
        instructions=base_context + """
        Use ScraperTool to extract content from FAQ pages.
        """,
        tools=[ScraperTool()],
        llm=chat_model,
    )

    workflow.add_agent(
        name="FinalResponder",
        role="Summarizes and formats final answer to user.",
        instructions=base_context + """
        Take all intermediate results and generate a clear and helpful response.
        """,
        llm=chat_model,
    )

    return workflow
