from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from personality import Personality, PersonalityType
from language import Language, LanguageChoice
from assignemt import Assignment
from circuit_breaker import CircuitBreaker
import asyncio

load_dotenv()
personality = Personality()
language = Language()
assignment = Assignment()
circuit_breaker = CircuitBreaker()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

app = FastAPI()

bulkhead_semaphore = asyncio.Semaphore(5)


class ChatRequest(BaseModel):
    user_input: str


@app.post("/chat")
async def chat(request: ChatRequest):
    initial_messages = [
        {"role": "system",
         "content": personality.get_personality(
             PersonalityType.NAPOLEON) + assignment.questionaire() + assignment.answer() + language.get_language(
             LanguageChoice.ENGLISH)},
        {"role": "user", "content": request.user_input}
    ]

    async with bulkhead_semaphore:
        try:
            chat_completion = circuit_breaker.call(
                client.chat.completions.create,
                model="gpt-4o-mini",
                messages=initial_messages
            )

            response_message = chat_completion.choices[0].message.content

            initial_messages.append({"role": "assistant", "content": response_message})

            return {"response": response_message}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in the API call: {e}")
