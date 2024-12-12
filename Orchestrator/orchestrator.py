import json

from config import Config
from rabbitmq_handler import RabbitMQHandler
from message_processor import MessageProcessor


def on_message_callback_channel_one(ch, method, properties, body):
    response = MessageProcessor.question_generator(body)
    rabbit_handler.send_reply(ch, properties, json.dumps(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def on_message_callback_channel_two(ch, method, properties, body):
    print("Received answer evaluation request")
    response = MessageProcessor.evaluate_answer(body)
    print("Sending answer evaluation response to rabbitmq...")
    rabbit_handler.send_reply(ch, properties, json.dumps(response))
    print("Sent answer evaluation response")
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    config = Config()
    rabbit_handler = RabbitMQHandler(config)

    # Setup RabbitMQ queues
    rabbit_handler.setup_queue(config.REQUEST_QUEUE)
    rabbit_handler.setup_queue(config.ANSWER_QUEUE)

    # Define consumers for each queue
    rabbit_handler.channel.basic_consume(
        queue=config.REQUEST_QUEUE, on_message_callback=on_message_callback_channel_one
    )
    rabbit_handler.channel.basic_consume(
        queue=config.ANSWER_QUEUE, on_message_callback=on_message_callback_channel_two
    )

    # Start consuming
    print("Starting RabbitMQ consumers...")
    rabbit_handler.channel.start_consuming()