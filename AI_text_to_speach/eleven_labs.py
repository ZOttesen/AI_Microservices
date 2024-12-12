import os
import asyncio
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from circuit_breaker import CircuitBreaker
from pathlib import Path  # Til håndtering af filnavne

# Load environment variables
load_dotenv()
XI_API_KEY = os.environ.get("XI_API_KEY")
CHUNK_SIZE = 1024
OUTPUT_DIR = "audio_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Bulkhead Pattern
bulkhead_semaphore = asyncio.Semaphore(5)

# FastAPI app
app = FastAPI()

# Circuit Breaker Instance
circuit_breaker = CircuitBreaker()

# Input model
class TTSRequest(BaseModel):
    text: str
    voice_id: str = "ohItIVrXTBI80RrUECOD"  # Default voice ID

# Eleven Labs TTS Function
def eleven_labs_tts(text, voice_id):
    print(f"Generating TTS for: {text}")
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 1,
            "use_speaker_boost": True
        }
    }

    audio_file_name = f"{hash(text)}.mp3"
    audio_file_path = os.path.join(OUTPUT_DIR, audio_file_name)

    print(f"Saving audio to: {audio_file_path}")

    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    if response.ok:
        with open(audio_file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        return audio_file_path
    else:
        raise Exception(f"Error from TTS service: {response.text}")

# TTS Endpoint
@app.post("/tts")
async def generate_tts(request: TTSRequest):
    async with bulkhead_semaphore:  # Bulkhead to limit concurrent calls
        try:
            print(f"Generating TTS for: {request.text}")
            # Call TTS function through Circuit Breaker
            audio_path = circuit_breaker.call(eleven_labs_tts, request.text, request.voice_id)
            return {"audio_url": f"/{audio_path}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))