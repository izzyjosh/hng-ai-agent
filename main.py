from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from models import A2AMessage, JSONRPCRequest, JSONRPCResponse
from agent import GrammarAgent

grammar_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global grammar_agent

    grammar_agent = GrammarAgent()

    yield

    if grammar_agent:
        grammar_agent = None

app = FastAPI(title="Grammar Agent", description="Ai agent for grammatical correction", version="1.0.0", lifespan=lifespan)

@app.post("/a2a/grammar-check")
async def grammar_check(request: Request):
    try:
        body = await request.json()

        if body.get("jsonrpc") != "2.0" or "id" not in body:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: jsonrpc must be '2.0' and id is required"
                    }
                }
            )
        rpc_request = JSONRPCRequest(**body)

        messages = []
        context_id = None
        task_id = None
        config = None


        if rpc_request.method == "message/send":
            messages = [rpc_request.params.message]
            config = rpc_request.params.configuration

        elif rpc_request.method == "execute":
            messages = rpc_request.params.messages
            context_id = rpc_request.params.contextId
            task_id = rpc_request.params.taskId

        result = await grammar_agent.run(
            message=messages,
            context_id=context_id,
            task_id=task_id,
            config=config
        )

        response = JSONRPCResponse(
            id=rpc_request.id,
            result=result
        )

        return response.model_dump()

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)

