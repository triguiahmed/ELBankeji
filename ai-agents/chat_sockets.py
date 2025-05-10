# websocket_router.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from beeai_framework.workflows.agent import AgentWorkflowInput
from multi_test import create_workflow
import time

router = APIRouter()

@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    user = websocket.query_params.get("user", "Anonymous")
    print("WebSocket connection established")
    date = time.strftime("%Y-%m-%d")
    time_now = time.strftime("%H:%M:%S")
    # 🟩 Initialize workflow ONCE globally
    workflow = create_workflow(user=user)
    await websocket.accept()
    try:
        while True:
            user_input = await websocket.receive_text()            
             
            base_context = f"""
            You are assisting user: {user}. Current date: {date}, time: {time_now}.
            You understand English, French, Arabic, and Tunisian dialect (mix between arabic and french sometimes).
            Always respond in the language or dialect used by the user.
            """
            
            result = await workflow.run(
                inputs=[
                    AgentWorkflowInput(
                        prompt=base_context + f"""
        Identify the user intent for this message: [USER MESSAGE START] {user_input}[USER MESSAGE END].
        
        - If it's transactional (e.g., balance check, transfer, transaction history), route to BankAgent.
        - If it's informational or policy-related (e.g., about banking products, obligations, or procedures), route to BankInfoAgent.
        - Always respond in the user's language or dialect.
                        """
                    ),
                ]
            )

            # Send final answer back
            await websocket.send_text(result.result.final_answer)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        import traceback
        traceback.print_exc()
        await websocket.send_text(f"Error: {str(e)}")
