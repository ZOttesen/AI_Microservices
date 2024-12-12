import os

class Config:
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    REQUEST_QUEUE = os.getenv("RABBITMQ_QUEUE", "request_queue")
    ANSWER_QUEUE = os.getenv("RABBITMQ_ANSWER_QUEUE", "answer_queue")
    TEXT_GENERATOR_URL = os.getenv("TEXT_GENERATOR_URL", "http://localhost:7000/chat")
    TTS_SERVICE_URL = os.getenv("TTS_SERVICE_URL", "http://localhost:7001/tts")
