import os
import json
import requests
import pika
from personality import PersonalityType  # Import PersonalityType
from language import LanguageChoice  # Import LanguageChoice

# Load environment variables
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE", "request_queue")
TEXT_GENERATOR_URL = os.getenv("TEXT_GENERATOR_URL", "http://localhost:7000/chat")
TTS_SERVICE_URL = os.getenv("TTS_SERVICE_URL", "http://localhost:7001/tts")

# RabbitMQ connection setup
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD),
    )
)
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)


def call_text_generator_service(category, points, preferences):
    try:
        payload = {
            "category": category,
            "points": points,
            "preferences": {
                "personality": preferences["personality"].value,
                "language": preferences["language"].value
            }
        }
        print(f"Sending payload to Text Generator: {json.dumps(payload, indent=2)}")

        response = requests.post(TEXT_GENERATOR_URL, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json().get("response")
        else:
            return {"error": f"Text Generator failed with status {response.status_code}"}
    except requests.RequestException as e:
        print(f"Error in Text Generator service: {e}")
        return {"error": "Service unavailable"}



def call_tts_service(text):
    try:
        response = requests.post(TTS_SERVICE_URL, json={"text": text})
        if response.status_code == 200:
            return response.json().get("audio_url")
        else:
            raise Exception(f"TTS service error: {response.text}")
    except requests.RequestException as e:
        print(f"Error in TTS service: {e}")
        return {"error": "Service unavailable"}


def on_message_callback(ch, method, properties, body):
    if not properties.reply_to or not properties.correlation_id:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Missing reply_to or correlation_id in message properties")
        return

    try:
        # Parse message from RabbitMQ
        message = json.loads(body)
        category = message.get("category")
        points = message.get("points")
        preferences = message.get("preferences", {})
        personality_type = preferences.get("personality", "Friendly")
        language_choice = preferences.get("language", "English")

        if not category or points is None:
            print("Invalid message: Missing 'category' or 'points'")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Validate and convert personality and language to enums
        try:
            personality_enum = PersonalityType[personality_type.upper()]
            language_enum = LanguageChoice[language_choice.upper()]
        except KeyError as e:
            print(f"Invalid personality or language in preferences: {e}")
            reply_message = json.dumps({"error": "Invalid personality or language"})
            ch.basic_publish(
                exchange="",
                routing_key=properties.reply_to,
                properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                body=reply_message
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Forbered preferences som dictionary
        preferences = {
            "personality": personality_enum,
            "language": language_enum
        }

        # Kald Text Generator Service med den nye struktur
        print(f"Calling Text Generator service with category: {category}, points: {points}, preferences: {preferences}")
        text_response = call_text_generator_service(category, points, preferences)

        # Handle Text Generator errors
        if isinstance(text_response, dict) and "error" in text_response:
            reply_message = json.dumps({"error": text_response["error"]})
            ch.basic_publish(
                exchange="",
                routing_key=properties.reply_to,
                properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                body=reply_message
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Call TTS service
        print("Calling TTS service...")
        try:
            tts_response = call_tts_service(text_response)

            if isinstance(tts_response, dict) and "error" in tts_response:
                reply_message = json.dumps({"error": tts_response["error"]})
                ch.basic_publish(
                    exchange="",
                    routing_key=properties.reply_to,
                    properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                    body=reply_message
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

        except Exception as e:
            print(f"Error in TTS service: {e}")
            reply_message = json.dumps({"error": f"TTS service error: {str(e)}"})
            ch.basic_publish(
                exchange="",
                routing_key=properties.reply_to,
                properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                body=reply_message
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Return both text and audio URL as response
        reply_message = json.dumps({
            "text": text_response,
            "audio_url": tts_response
        })

        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=reply_message
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


# Consume messages from the queue
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message_callback)

print("Listening for messages on RabbitMQ...")
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Shutting down...")
    connection.close()
