import asyncio
import json
import time
import traceback

from beeai_framework.backend.chat import ChatModel
from beeai_framework.context import RunContext
from beeai_framework.emitter.emitter import Emitter
from beeai_framework.logger import Logger
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

class GetBalanceToolInput(BaseModel):
    user: str

class GetBalanceTool(Tool[GetBalanceToolInput, ToolRunOptions, StringToolOutput]):
    name = "GetBalanceTool"
    description = "Get user's account balance"
    input_schema = GetBalanceToolInput

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        super().__init__(options)
        self.bank_client = BankAPIClient()

    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(namespace=["tool", "bank"], creator=self)

    async def _run(self, input: GetBalanceToolInput, options: ToolRunOptions | None, context: RunContext) -> StringToolOutput:
        try:
            result = self.bank_client.get_balance(input.user)
            return StringToolOutput(json.dumps(result))
        except Exception as e:
            logger.error(f"Error in GetBalanceTool: {e}")
            raise ToolInputValidationError(f"Banking operation failed GetBalanceTool: {e}")

class MakeTransferToolInput(BaseModel):
    user: str
    amount: Optional[float]
    receiver: Optional[str]

class MakeTransferTool(Tool[MakeTransferToolInput, ToolRunOptions, StringToolOutput]):
    name = "MakeTransferTool"
    description = "Make money transfer from user account to another"
    input_schema = MakeTransferToolInput

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        super().__init__(options)
        self.bank_client = BankAPIClient()

    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(namespace=["tool", "bank"], creator=self)

    async def _run(self, input: MakeTransferToolInput, options: ToolRunOptions | None, context: RunContext) -> StringToolOutput:
        try:
            if input.amount is None or input.receiver is None:
                raise ToolInputValidationError("Amount and receiver are required for transfer.")
            result = self.bank_client.send_money(input.user, input.receiver, input.amount)
            return StringToolOutput(json.dumps(result))
        except Exception as e:
            logger.error(f"Error in MakeTransferTool: {e}")
            raise ToolInputValidationError(f"Banking operation failed MakeTransferTool: {e}")

class GetTransactionHistoryToolInput(BaseModel):
    user: str

class GetTransactionHistoryTool(Tool[GetTransactionHistoryToolInput, ToolRunOptions, StringToolOutput]):
    name = "GetTransactionHistoryTool"
    description = "Get Transactions History of a user account"
    input_schema = GetTransactionHistoryToolInput

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        super().__init__(options)
        self.bank_client = BankAPIClient()

    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(namespace=["tool", "bank"], creator=self)

    async def _run(self, input: GetTransactionHistoryToolInput, options: ToolRunOptions | None, context: RunContext) -> StringToolOutput:
        try:
            result = self.bank_client.get_transactions_history(input.user)
            return StringToolOutput(json.dumps(result))
        except Exception as e:
            logger.error(f"Error in GetTransactionHistoryTool: {e}")
            raise ToolInputValidationError(f"Banking operation failed GetTransactionHistoryTool: {e}")

class RequestLoanToolInput(BaseModel):
    user: str
    amount: Optional[float]

class RequestLoanTool(Tool[RequestLoanToolInput, ToolRunOptions, StringToolOutput]):
    name = "RequestLoanTool"
    description = "Request a loan amount for a user"
    input_schema = RequestLoanToolInput

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        super().__init__(options)
        self.bank_client = BankAPIClient()

    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(namespace=["tool", "bank"], creator=self)

    async def _run(self, input: RequestLoanToolInput, options: ToolRunOptions | None, context: RunContext) -> StringToolOutput:
        try:
            if input.amount is None:
                raise ToolInputValidationError("Amount is required for loan.")
            result = self.bank_client.request_loan(input.user, input.amount)
            return StringToolOutput(json.dumps(result))
        except Exception as e:
            logger.error(f"Error in RequestLoanTool: {e}")
            raise ToolInputValidationError(f"Banking operation failed RequestLoanTool: {e}")

# ---- WORKFLOW CREATION ----
def create_workflow(user: str) -> AgentWorkflow:
    chat_model = ChatModel.from_name("ollama:granite3.2:2b-instruct-q4_K_M")
    workflow = AgentWorkflow(name="Multi-agent Smart Banking Assistant")

    local_time = time.localtime()
    date = time.strftime("%Y-%m-%d", local_time)
    time_now = time.strftime("%H:%M", local_time)

    base_context = f"""
You are assisting user: {user}. Current date: {date}, time: {time_now}.
You understand English, French, Arabic, and Tunisian dialects.
Always respond using the same language or dialect the user used.
"""

    # BankAgent
    workflow.add_agent(
        name="BankAgent",
        role="Handles transactional banking requests.",
        instructions=base_context + """
You are a multilingual smart banking assistant that handles transactional banking tasks (like checking balance, making transfers, and showing history).

Your goal is to recognize user intent clearly and accurately execute banking actions using the tools provided:
- Use `GetBalanceTool` if user asks about how much money is in their account.
- Use `GetTransactionHistoryTool` if user asks for their past transactions or history.
- Use `MakeTransferTool` if the user wants to send money to someone.
- Use `RequestLoanTool` if the user wants a loan.

You must identify user intent even when expressed in:
- English
- French
- Arabic (MSA or Tunisian dialect)

Respond with clear and actionable information in the same language or dialect used by the user.
""",
        tools=[GetTransactionHistoryTool(), MakeTransferTool(), GetBalanceTool(), RequestLoanTool()],
        llm=chat_model,
    )

    # FAQScraper
    workflow.add_agent(
        name="FAQScraper",
        role="Scrapes bank FAQs to answer policy-related questions.",
        instructions=base_context + """
You are a multilingual FAQ assistant. Your goal is to answer questions about banking policies, procedures, or general bank information (e.g., loan eligibility, document requirements).

If the user's question is about:
- policies
- procedures
- bank offerings
- product information

Then:
1. Use `ScraperTool()` to fetch answers from the following sources:
    - https://www.biat.com.tn/faq
    - https://www.banquezitouna.com/fr/faq
    - https://www.bank-abc.com/fr/CountrySites/Tunis/AboutABC/faqs

Do not answer questions related to personal accounts or transactions.

Always respond in the same language or dialect the user used.
""",
        tools=[ScraperTool()],
        llm=chat_model,
    )

    # FinalResponder
    workflow.add_agent(
        name="FinalResponder",
        role="Formats and delivers final response to the user.",
        instructions=base_context + """
You are the final output agent. Your role is to:
- Receive intermediate agent results.
- Format a helpful and friendly response to the user.
- Always respond using the same language or dialect the user used in the original message.
- Be concise, clear, and respectful.

If information is missing or incomplete, politely state that.
""",
        llm=chat_model,
    )

    return workflow

# ---- MAIN WORKFLOW ----
async def main():
    user = "John Doe"
    workflow = create_workflow(user)

    user_icon = "👤"
    agent_icon = "🏦"

    result = None
    user_input = input(f"{user_icon} USER ({user}): ")

    local_time = time.localtime()
    date = time.strftime("%Y-%m-%d", local_time)
    time_now = time.strftime("%H:%M", local_time)

    base_context = f"""
You are assisting user: {user}. Current date: {date}, time: {time_now}.
You understand English, French, Arabic, and Tunisian dialects.
Always respond using the same language or dialect the user used.
"""

    result = await workflow.run(
        inputs=[
            AgentWorkflowInput(
                prompt=base_context + f"""
Analyze this user message: '{user_input}'.
Detect the user’s intent (e.g., check balance, see transactions, send money, ask FAQ).
Identify the language or dialect used, and route to the proper agent.
Ensure the final response is in the same language or dialect.
"""
            ),
        ]
    )

    print(f"{agent_icon} AGENT: {result.result.final_answer}")

# ---- ENTRY POINT ----
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        traceback.print_exc()
