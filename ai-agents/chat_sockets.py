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

    # 🟩 Initialize workflow ONCE globally
    workflow = create_workflow(user=user)
    await websocket.accept()
    try:
        while True:
            user_input = await websocket.receive_text()

            local_time = time.localtime()
            date = time.strftime("%Y-%m-%d", local_time)
            time_now = time.strftime("%H:%M", local_time)      
        
            result = await workflow.run(
                inputs=[
                    AgentWorkflowInput(
                    prompt=f"""
                    You are assisting the user: {user}. Current date: {date}, time: {time_now}.
                    You understand English, French, Arabic, and Tunisian dialect (mix between arabic and french sometimes).
                    Identify the user intent for this message: [USER MESSAGE START]{user_input}[USER MESSAGE END].
                    - If it's transactional (e.g., balance check, transfer, transaction history) respond.
                    
                    - Always respond in the user's language or dialect.
                    """
                    ),
                    AgentWorkflowInput(
                            prompt=f"""
                            You understand English, French, Arabic, and Tunisian dialect (mix between arabic and french sometimes).
                            Identify the user intent for this message: [USER MESSAGE START]{user_input}[USER MESSAGE END].
                            - If it's informational or policy-related (e.g., about banking products, obligations, or procedures), route to BankInfoAgent.
                        
                            - Always respond in the user's language or dialect.
                            """
                            ),
                     AgentWorkflowInput(
                            prompt=f"Summarize the response for {user_input}.",
                            expected_output=f"A paragraph that respond to {user_input} in the user's language or dialect.",
                        ),
                ]
            )

            # Send final answer back
            logger.info("Response {}".format(result.result.final_answer))
            await websocket.send_text(result.result.final_answer)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        import traceback
        traceback.print_exc()
        await websocket.send_text(f"Error: {str(e)}")
