import pika

class RabbitMQHandler:
    def __init__(self, config):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config.RABBITMQ_HOST,
                port=config.RABBITMQ_PORT,
                credentials=pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD),
            )
        )
        self.channel = self.connection.channel()

    def setup_queue(self, queue_name):
        self.channel.queue_declare(queue=queue_name)

    def consume(self, queue_name, callback):
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback)
        print(f"Listening for messages on queue: {queue_name}")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Shutting down...")
            self.connection.close()

    def send_reply(self, ch, properties, body):
        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=body,
        )
