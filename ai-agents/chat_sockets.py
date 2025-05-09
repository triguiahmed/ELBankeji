# websocket_router.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from beeai_framework.workflows.agent import AgentWorkflowInput
from multi_test import create_workflow

router = APIRouter()



@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    
    print("WebSocket connection established")
    
    # 🟩 Initialize workflow ONCE globally
    workflow = create_workflow(user="John Doe")
    await websocket.accept()
    try:
        while True:
            user_input = await websocket.receive_text()
            print(f"👤 USER: {user_input}")

            # Run the workflow for each message
            result = await workflow.run(
                inputs=[
                    AgentWorkflowInput(prompt=user_input),
                    AgentWorkflowInput(prompt=f"[Synthesizer] Summarize and reply to: {user_input}")
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