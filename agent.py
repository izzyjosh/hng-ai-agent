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


        user_message = message.parts

        if not user_message:
            raise ValueError("No message provided")

        user_message = user_message[-1].data[-1]

        user_text = "" 
        if user_message["kind"] == "text":
            user_text = user_message["text"].strip() if user_message["text"] else None

            if not user_text:
                raise ValueError("No text provided")

        try:
            response = await self.agent.run(user_prompt=user_text)

            response_message = A2AMessage(
                    role="agent",
                    parts=[MessagePart(kind="text", text=response.output.model_dump_json())],
                    taskId=task_id
                    )
            history = []
            history = history.append(message)
            history = history.append(response_message)
            
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
