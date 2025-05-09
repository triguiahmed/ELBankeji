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

# ---- MAIN WORKFLOW ----
async def main():
    chat_model = ChatModel.from_name("ollama:granite3.2:2b-instruct-q4_K_M")
    workflow = AgentWorkflow(name="Multi-agent Smart Banking Assistant")

    user = "John Doe"
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
        Only interfere when the goal is to make banking actions:
        - make-transfer (amount and receiver required)
        - get-balance
        - get-transaction-history
        """,
        tools=[BankTool()],
        llm=chat_model,
    )

    workflow.add_agent(
        name="FAQScraper",
        role="Scrapes bank FAQs to answer banking related question queries.",
        instructions=base_context + """
        Only interfere when asked about banking policies or general info, you have FAQ URL pages to extract data from:
        - https://www.biat.com.tn/faq
        - https://www.banquezitouna.com/fr/faq
        - https://www.bank-abc.com/fr/CountrySites/Tunis/AboutABC/faqs

        """,
        tools=[ScraperTool()],
        llm=chat_model,
    )

    workflow.add_agent(
        name="FinalResponder",
        role="Summarizes and formats final answer to user.",
        instructions=base_context + """
        Take all intermediate results and generate a clear and helpful response in the same language or dialect of the input.
        """,
        llm=chat_model,
    )

    user_icon = "👤"
    agent_icon = "🏦"

    while True:
        result=None
        user_input = input(f"{user_icon} USER ({user}): ")

        result = await workflow.run(
            inputs=[
                AgentWorkflowInput(prompt=user_input),
                AgentWorkflowInput(prompt=f"Summarize everything of {user_input} and class the intent to an action request or question to respond and pass the intent to the other agents.  "),
            ]
        )

        print(f"{agent_icon} AGENT: {result.result.final_answer}")

# ---- ENTRY POINT ----
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        traceback.print_exc()
#python bank_agent.py 

#               how much money do i have in my account ?
#                   combien j'ai de l'argent dans mon compte bancaire
#                   كم عندي مال في الحساب 
#                 قداه عندي فلوس


#                 what is my transaction history?
#                 Donner moi mon historique de transaction?
#                 اعطيني historique متاعي




#   I want to send 200 to Jane Smith
#   Je veux envoyer 200 à Jane Smith
#   نحب نبعث 200 لـ Jane Smith



#Scraping
#LA BIAT EMET-ELLE DES OBLIGATIONS ?