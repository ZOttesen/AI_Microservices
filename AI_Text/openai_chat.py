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

class Preferences(BaseModel):
    personality: PersonalityType
    language: LanguageChoice

class ChatRequest(BaseModel):
    category: str
    points: int
    preferences: Preferences

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Sæt personlighed og sprog baseret på input
        personality.set_personality(request.preferences.personality)
        language.set_language(request.preferences.language)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generer initiale beskeder baseret på kategori og point
    initial_messages = [
        {"role": "system", "content": personality.get_personality() + assignment.questionnaire() + assignment.answer() + language.get_language()},
        {"role": "user", "content": request.category + str(request.points)}
    ]

    async with bulkhead_semaphore:
        try:
            # Foretag et API-kald til OpenAI
            chat_completion = circuit_breaker.call(
                openai.ChatCompletion.create,
                model="gpt-4o-mini",
                messages=initial_messages
            )

            response_message = chat_completion["choices"][0]["message"]["content"]

            return {"response": response_message}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in the API call: {e}")
