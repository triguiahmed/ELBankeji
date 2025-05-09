@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    # Get user from query parameters
    user = websocket.query_params.get("user", "Anonymous")
    print(f"WebSocket connection established for user: {user}")

    await websocket.accept()

    # Initialize workflow WITH user
    workflow = create_workflow(user=user)
    
    try:
        while True:
            user_input = await websocket.receive_text()
            print(f"👤 USER ({user}): {user_input}")

            result = await workflow.run(
                inputs=[
                    AgentWorkflowInput(prompt=user_input),
                    AgentWorkflowInput(prompt=f"[Synthesizer] Summarize and reply to: {user_input}")
                ]
            )

            await websocket.send_text(result.result.final_answer)

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user: {user}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_text(f"Error: {str(e)}")
        except:
            pass
