from pydantic import BaseModel, Field, Optional
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

import asyncio

from service import BankAPIClient  # Assuming it's in service.py

logger = Logger(__name__)

class BankToolInput(BaseModel):
    action: Literal["loan", "transfer", "balance", "history"]
    user: Optional[str] = None
    amount: Optional[float] = None
    receiver: Optional[str] = None
    date: Optional[str] = None  # ISO format

class BankTool(Tool[BankToolInput, ToolRunOptions, StringToolOutput]):
    name = "BankTool"
    description = "Interact with the banking API to retrieve balances, make transfers, request loans, and view transaction history."
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
            if input.action == "loan":
                result = self.bank_client.request_loan(input.user, input.amount)
            elif input.action == "transfer":
                result = self.bank_client.send_money(input.user, input.receiver, input.amount)
            elif input.action == "balance":
                result = self.bank_client.get_balance(input.user)
            elif input.action == "history":
                from datetime import datetime
                parsed_date = datetime.fromisoformat(input.date) if input.date else None
                result = self.bank_client.get_transactions_history(input.user, input.receiver, parsed_date)
            else:
                raise ToolInputValidationError("Invalid action provided.")
            return StringToolOutput(json.dumps(result))
        except Exception as e:
            logger.error(f"Error in BankTool: {e}")
            raise ToolInputValidationError(f"Failed to perform banking operation: {e}")
async def main() -> None:
    chat_model = ChatModel.from_name("ollama:granite3.2:2b-instruct-q4_K_M")
    bank_tool = BankTool()
    agent = ReActAgent(llm=chat_model, tools=[bank_tool], memory=UnconstrainedMemory(), stream=True)

    instructions = """
    You are a smart banking assistant. Given customer questions or commands, use the banking API to:

    - Retrieve current balances
    - Transfer money between accounts
    - Request new loans
    - Review transaction history for a specific date

    Identify key actions from the user input. Your tool input must be structured with:
    - action: one of [loan, transfer, balance, history]
    - user: sender or account holder
    - receiver: for transfers or history
    - amount: for loan or transfer
    - date: ISO format (optional, for history)

    Your job is to interpret natural language and call the right tool action.

    Example: "Can you send 200 to alice from john?" -> transfer, user=john, receiver=alice, amount=200

    Respond clearly and informatively with the result.
    """

    user_icon = "👤"
    agent_icon = "🏦"

    await agent.memory.add(SystemMessage(content=instructions))

    prompt = input(f"{user_icon} USER: ")
    result = await agent.run(prompt)
    print(f"{agent_icon} AGENT: {result.result.text}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        traceback.print_exc()
