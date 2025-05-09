from pydantic import BaseModel, Field
from typing import Any, Literal
import json
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
from typing import Optional
from newspaper import Article  # library to extract readable content

import asyncio

from bank_service import BankAPIClient  # Assuming it's in service.py

logger = Logger(__name__)

class BankToolInput(BaseModel):
    """
        Represents an action performed by a user in a banking system.

        - "request-loan": Ask for a loan (requires `amount`)
        - "make-transfer": Send money to another user (requires `amount` and `receiver`)
        - "get-balance": Get current account balance
        - "get-transaction-history": View the list of past transactions
    """
    action: Literal["request-loan", "make-transfer", "get-balance", "get-transaction-history"]
    user: str 
    amount: Optional[float] 
    receiver: Optional[str] 

class ScraperToolInput(BaseModel):
    url: str

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
            result = {
                "title": article.title,
                "text": article.text
            }
            return StringToolOutput(json.dumps(result))
        except Exception as e:
            traceback.print_exc()
            return StringToolOutput(json.dumps({"error": f"Failed to scrape {input.url}: {str(e)}"}))

class BankTool(Tool[BankToolInput, ToolRunOptions, StringToolOutput]):
    name = "BankTool"
    description = (
    "This tool allows users to perform banking operations:\n"
    "- 'request-loan': Request a loan (needs 'amount')\n"
    "- 'make-transfer': Transfer funds (needs 'amount' and 'receiver')\n"
    "- 'get-balance': Show current account balance\n"
    "- 'get-transaction-history': Show the user's transaction history"
)
    input_schema = BankToolInput

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        super().__init__(options)
        self.bank_client = BankAPIClient()

    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(
            namespace=["tool", "bank"],
            creator=self,
        )

    async def _run(self, input: BankToolInput, options: ToolRunOptions | None, context: RunContext) -> StringToolOutput:
        try:
            print("## TOOOL INPUT")
            print(input)
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
            raise ToolInputValidationError(f"Failed to perform banking operation: {e}")

async def main() -> None:
    chat_model = ChatModel.from_name("ollama:granite3.2:2b-instruct-q4_K_M")
    bank_tool = BankTool()
    scraper_tool = ScraperTool()
    agent = ReActAgent(llm=chat_model, tools=[bank_tool, scraper_tool], memory=UnconstrainedMemory(), stream=True)
    user = "John Doe"
    import time
    local_time = time.localtime()
    date = time.strftime("%Y-%m-%d", local_time)
    time_now = time.strftime("%H:%M", local_time)
    
    instructions = f"""
        the date time now : {time_now}
        You are a smart banking assistant you are interacting with the user: "{user}".



        You understand English, French, Arabic and Tunisian dialect (very similar to arabic and french)
        Respond clearly and informatively with the result in the same language spoken by the user.
    """

    user_icon = "👤"
    agent_icon = "🏦"
    
    await agent.memory.add(SystemMessage(content=instructions))
    await agent.memory.add(SystemMessage(content="""
            You can use the 'BankTool' to handle user requests related to banking actions.

            Available actions:
            - 'request-loan': Request a loan amount
            - 'make-transfer': Transfer money to another person
            - 'get-balance': Display account balance
            - 'get-transaction-history': List past transactions (date, amount, type)

            Only use the tool when needed and only fill the necessary fields.
            """))

    await agent.memory.add(SystemMessage(content="""
            You can use the 'ScraperTool' to handle user requests related to FAQs.

            these are FAQs URL to scrape if needed:
            https://www.biat.com.tn/faq

            Only use the tool when needed and only fill the necessary fields.
            """))





     ####



    # await agent.memory.add(SystemMessage(content=faqs))
    while True:
        prompt = input(f"{user_icon} USER (John Doe): ")
        result = await agent.run(prompt)
        print(f"{agent_icon} AGENT: {result.result.text}")
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        traceback.print_exc()
