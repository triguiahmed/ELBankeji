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

import asyncio

from bank_service import BankAPIClient  # Assuming it's in service.py

logger = Logger(__name__)

class BankToolInput(BaseModel):
    action: Literal["loan", "transfer", "balance", "history"]
    user: str = Field(description="The username of the connected user.")
    amount: Optional[float] = Field(default=None, description="Amount of money involved, if applicable.")
    receiver: Optional[str] = Field(default=None, description="Receiver of the money, if applicable.")



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
                if input.amount is None:
                    raise ToolInputValidationError("Amount is required for loan.")
                result = self.bank_client.request_loan(input.user, input.amount)

            elif input.action == "transfer":
                if input.amount is None or input.receiver is None:
                    raise ToolInputValidationError("Amount and receiver are required for transfer.")
                result = self.bank_client.send_money(input.user, input.receiver, input.amount)

            elif input.action == "balance":
                result = self.bank_client.get_balance(input.user)

            elif input.action == "history":
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
    agent = ReActAgent(llm=chat_model, tools=[bank_tool], memory=UnconstrainedMemory(), stream=True)
    user = "John Doe"
    import time
    local_time = time.localtime()
    date = time.strftime("%Y-%m-%d", local_time)
    time_now = time.strftime("%H:%M", local_time)
    
    instructions = f"""
    You are a smart and helpful banking assistant, interacting with the user: "{user}".
    The current date and time is: {time_now}.
    You understand and can respond in English, French, Arabic, and the Tunisian dialect (which closely resembles Arabic and French).
    Always reply clearly and informatively, using the same language that the user speaks.
    Use the appropriate banking tool action when needed. Available actions are:
    - 'loan': Request a loan of a specified amount.
    - 'transfer': Send money to another user by specifying the amount and receiver.
    - 'balance': Check the current account balance.
    - 'history': Retrieve the user's transaction history (does not require amount or receiver).

    Only request information from the user that is necessary for the chosen action.
    Respond in a concise, friendly, and accurate manner.
    """

    user_icon = "👤"
    agent_icon = "🏦"

    await agent.memory.add(SystemMessage(content=instructions))
    while True:
        prompt = input(f"{user_icon} USER (John Doe): ")
        result = await agent.run(prompt)
        print(f"{agent_icon} AGENT: {result.result.text}")
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        traceback.print_exc()
#python bank_agent.py 

#how much money do i have in my account ?
#combien j'ai de l'argent dans mon compte bancaire
#كم عندي مال في الحساب 
#قداه عندي فلوس


#what is my transaction history?
#Donner moi mon historique de transaction?
#اعطيني سجل حسابي البنكي
#اعطيني historique متاعي


