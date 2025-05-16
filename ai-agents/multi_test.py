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
from bs4 import BeautifulSoup
import requests
import logging
 
class ScraperTool(Tool[ScraperToolInput, ToolRunOptions, StringToolOutput]):
    name = "ScraperTool"
    description = "Extracts and returns main informational content from a banking FAQ or information page."
    input_schema = ScraperToolInput
 
    def __init__(self, options: dict[str, any] | None = None):
        super().__init__(options)
        self.logger = logging.getLogger("ScraperTool")
 
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
    description = (
        "Get user's account balance"
    )
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
    description = (
        "Make money transfer from user account to another"
    )
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
    description = (
        "Get Transactions History of a user account"
    )
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
    description = (
        "Request a loan amount for a user"
    )
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
 
# ---- MAIN WORKFLOW ----
def create_workflow(user: str) -> AgentWorkflow:
    import os
    os.environ["OLLAMA_API_BASE"] =  "http://host.docker.internal:11434"
    chat_model = ChatModel.from_name("ollama:granite3.2:2b-instruct-q4_K_M")

    logger.info("Settings")
    logger.info(chat_model._settings)
    workflow = AgentWorkflow(name="Multi-agent Smart Banking Assistant")
 
    local_time = time.localtime()
    date = time.strftime("%Y-%m-%d", local_time)
    time_now = time.strftime("%H:%M", local_time)
    workflow.add_agent(
        name="BankAgent",
        role="BankAgent that Handles transactional banking requests.",
        instructions="""
        Only handle transactional requests:
        - Check account balance
        - View transaction history
        - Make a money transfer
        - Request a loan
 
        Do NOT interfere to:
        - Questions about banking products, policies, procedures
        - Legal information
        - FAQ-related topics
         """,
        tools=[
            GetTransactionHistoryTool(),
            MakeTransferTool(),
            GetBalanceTool(),
            RequestLoanTool(),
        ],
        llm=chat_model,
    )

    workflow.add_agent(
        name="BankInfoAgent",
        role="BankInfoAgent that answers questions about banking policies, products, and procedures using FAQ pages.",
        instructions="""
        Handle user questions related to banking policies, products, and general information.

        Use the ScraperTool to search the following FAQ pages:
        - https://www.biat.com.tn/faq
        - https://www.banquezitouna.com/fr/faq
        - https://www.bank-abc.com/fr/CountrySites/Tunis/AboutABC/faqs
        Do NOT interfere to:
        - Check account balance
        - View transaction history
        - Make a money transfer
        - Request a loan
        """,
        tools=[ScraperTool()],
        llm=chat_model,
    )
    workflow.add_agent(
        name="DataSynthesizer",
        role="A meticulous and creative data synthesizer",
        instructions="""You can combine disparate information into a final coherent summary."
        Respond with a clear answer in the user's language. If no relevant info is found, politely say so.""",
        llm=chat_model,
    )
 
    return workflow

#python bank_agent.py
 
#               how much money do i have in my account ?
#                   combien j'ai de l'argent dans mon compte bancaire
#                   كم عندي مال في الحساب
#                 قداه عندي فلوس في compte
 
 
#                 what is my transaction history?
#                 Donner moi mon historique de transaction?
#                 اعطيني historique متاعي
 
 
 
 
#   I want to send 200 to Jane Smith
#   Je veux envoyer 200 à Jane Smith
#   نحب نبعث 200 لـ Jane Smith
 
 
 
#Scraping
#LA BIAT EMET-ELLE DES OBLIGATIONS ?
 