import requests
import json
import os
from dotenv import load_dotenv


load_dotenv()
xi_api_key = os.environ.get("XI_API_KEY")

CHUNK_SIZE = 1024
VOICE_ID = "ohItIVrXTBI80RrUECOD"  # ID of the voice model to use
TEXT_TO_SPEAK = """
(angry)What the fuck did you just say to me you imbisul
</voice>
"""

OUTPUT_PATH = "output.mp3"  # Path to save the output audio file

# Construct the URL for the Text-to-Speech API request
tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

# Set up headers for the API request, including the API key for authentication
headers = {
    "Accept": "application/json",
    "xi-api-key": xi_api_key
}

# Set up the data payload for the API request, including the text and voice settings
data = {
    "text": TEXT_TO_SPEAK,
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0,  # Lavere værdi for mere følelsesmæssig variation
        "similarity_boost": 0,  # Lidt lavere for mere frihed i udtrykket
        "style": 1,
        "use_speaker_boost": True

    }
}

# Make the POST request to the TTS API with headers and data, enabling streaming response
response = requests.post(tts_url, headers=headers, json=data, stream=True)

# Check if the request was successful
if response.ok:
    # Open the output file in write-binary mode
    with open(OUTPUT_PATH, "wb") as f:
        # Read the response in chunks and write to the file
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)
    # Inform the user of success
    print("Audio stream saved successfully.")
else:
    # Print the error message if the request was not successful
    print(response.text)