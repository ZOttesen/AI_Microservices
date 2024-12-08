import openai  # Importer openai direkte
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from personality import Personality, PersonalityType
from language import Language, LanguageChoice
from assignemt import Assignment
from circuit_breaker import CircuitBreaker
import asyncio

# Load miljøvariabler fra .env-fil
load_dotenv()

# Indstil API-nøglen fra miljøvariablerne
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialisering af klasser
personality = Personality()
language = Language()
assignment = Assignment()
circuit_breaker = CircuitBreaker()

# Opret FastAPI-applikationen
app = FastAPI()

# Begræns samtidige anmodninger
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
            # Foretag et API-kald til OpenAI
            chat_completion = circuit_breaker.call(
                openai.ChatCompletion.create,  # Brug korrekt metode fra OpenAI SDK
                model="gpt-4",  # Brug en gyldig model
                messages=initial_messages
            )

            response_message = chat_completion["choices"][0]["message"]["content"]

            initial_messages.append({"role": "assistant", "content": response_message})

            return {"response": response_message}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in the API call: {e}")
