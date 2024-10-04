from openai import OpenAI
import os
from dotenv import load_dotenv
from personality import Personality
from language import Language
from assignemt import Assignment

load_dotenv()
personality = Personality()
language = Language()
assignment = Assignment()



# https://github.com/openai/openai-python
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

initial_messages = [
    {"role": "system", "content": personality.napoleon() + assignment.questionaire() + assignment.answer() + language.english()},
    {"role": "user", "content": "Movies, 10"}
]

chat_completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=initial_messages
)

response_message = chat_completion.choices[0].message.content
print(response_message)

# Tilføj det første svar til samtaleloggen
initial_messages.append({"role": "assistant", "content": response_message})

# Vent på brugerinput
user_input = input("Skriv dit svar: ")

# Tilføj brugerens input til samtaleloggen
initial_messages.append({"role": "user", "content": user_input})

# Andet API-kald med hele samtaleloggen
chat_completion2 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=initial_messages
)

response_message2 = chat_completion2.choices[0].message.content
print(response_message2)