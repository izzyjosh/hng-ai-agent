# Python import
import os
from typing import List, Optional
from uuid import uuid4

# Library import 
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from dotenv import load_dotenv
from fastapi.exceptions import HTTPException

# Module import
from models import A2AMessage, GrammarResponse, MessageConfiguration, MessagePart, TaskResult, TaskStatus

load_dotenv()


class GrammarAgent:
    SYSTEM_INSTRUCTIONS = (
            "You are a specialized assistant that helps users correct grammar, spelling, "
            "and phrasing mistakes in text"
            "Your goal is to return correct sentence and explanation"
            "If users provides unrelated topics, politely state that you can only help with grammar or writing task"
            )

    def __init__(self):

        provider = GoogleProvider(api_key=os.getenv("GOOGLE_API_KEY", "no Key"))

        model = GoogleModel("gemini-2.0-flash", provider=provider)

        self.agent = Agent(
                model=model,
                output_type=GrammarResponse,
                system_prompt=self.SYSTEM_INSTRUCTIONS
                )

    async def run(self, message: A2AMessage, context_id: Optional[str] = None, task_id: Optional[str] = None, config: Optional[MessageConfiguration] = None):

        context_id = context_id or str(uuid4())
        task_id = task_id or str(uuid4())

        user_messages = message.parts

        if not user_messages:
            raise ValueError("No message provided")

        # handle last message part
        last_part = user_messages[-1]

        user_text = ""

        if hasattr(last_part, "kind") and last_part.kind == "text":
            user_text = getattr(last_part, "text", "")
        elif hasattr(last_part, "data") and last_part.data:
            data_part = last_part.data[-1]
            if isinstance(data_part, dict) and data_part.get("kind") == "text":
                user_text = data_part.get("text", "").strip()
        else:
            user_text = ""

        if not user_text:
            raise ValueError("No text provided")

        try:
            response = await self.agent.run(user_prompt=user_text)

            response_message = A2AMessage(
                    role="agent",
                    parts=[MessagePart(kind="text", text=response.output.model_dump_json())],
                    taskId=task_id
                    )
            history = [message, response_message]
             
            task_result = TaskResult(
                    id=task_id,
                    contextId=context_id,
                    status=TaskStatus(state="completed", message=response_message),
                    history=history
                    )

            return task_result
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"internal server error: {str(e)}")
