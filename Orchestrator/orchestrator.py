import json
import requests
import pika

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "request_queue"
RABBITMQ_USER = 'user'
RABBITMQ_PASSWORD = 'password'

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    )
)

channel = connection.channel()

channel.queue_declare(queue=QUEUE_NAME)


def call_text_generator_service(user_input):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat",  # Text Generator service endpoint
            json={"user_input": user_input},
            timeout=10  # Timeout for HTTP-kald
        )
        if response.status_code == 200:
            return response.json().get("response")  # Returnerer svaret fra Text Generator
        else:
            return {"error": f"Text Generator failed with status {response.status_code}"}

    except requests.RequestException as e:
        print(f"Error in Text Generator service: {e}")
        return {"error": "Service unavailable"}


def call_tts_service(text):
    tts_url = "http://localhost:8001/tts"
    response = requests.post(tts_url, json={"text": text})
    if response.status_code == 200:
        return response.json().get("audio_url")
    else:
        raise Exception(f"TTS service error: {response.text}")


def on_message_callback(ch, method, properties, body):
    if not properties.reply_to or not properties.correlation_id:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Missing reply_to or correlation_id in message properties")
        return

    try:
        # Parse besked fra RabbitMQ
        message = json.loads(body)
        user_input = message.get("text")

        if not user_input:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print("Invalid message received, missing 'text'")
            return

        # Trin 1: Kald Text Generator service
        print("Calling Text Generator service...")
        text_response = call_text_generator_service(user_input)

        # Hvis Text Generator fejler, returner en fejlbesked
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

        # Trin 2: Send teksten til TTS-tjenesten
        print("Calling TTS service...")
        try:
            tts_response = call_tts_service(text_response)

            # Hvis TTS fejler, returner en fejlbesked
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

        # Trin 3: Returnér både tekst og lyd-URL som svar
        reply_message = json.dumps({
            "text": text_response,  # Teksten fra Text Generator
            "audio_url": tts_response  # Lyd-URL'en fra TTS
        })

        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=reply_message
        )

        # Anerkend beskeden
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


# Forbrug beskeder fra køen
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message_callback)

print("Listening for messages on RabbitMQ...")
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Shutting down...")
    connection.close()
