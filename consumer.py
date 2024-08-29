# import logging
import json
import os
#
from confluent_kafka import Consumer

# import logging_config
# import utils


# class ConsumerClass:
#     def __init__(self, bootstrap_server, topic, group_id):
#         """Initializes the consumer."""
#         self.bootstrap_server = bootstrap_server
#         self.topic = topic
#         self.group_id = group_id
#         self.consumer = Consumer(
#             {"bootstrap.servers": bootstrap_server, "group.id": self.group_id}
#         )
#
#     def consume_messages(self):
#         """Consume Messages from Kafka."""
#         self.consumer.subscribe([self.topic])
#         logging.info(f"Successfully subscribed to topic: {self.topic}")
#
#         try:
#             while True:
#                 msg = self.consumer.poll(1.0)
#                 if msg is None:
#                     continue
#                 if msg.error():
#                     logging.error(f"Consumer error: {msg.error()}")
#                     continue
#                 byte_message = msg.value()
#                 decoded_message = byte_message.decode("utf-8")
#                 logging.info(
#                     f"Byte message: {byte_message}, Type: {type(byte_message)}"
#                 )
#                 logging.info(
#                     f"Decoded message: {decoded_message}, Type: {type(decoded_message)}"  # noqa: E501
#                 )
#         except KeyboardInterrupt:
#             pass
#         finally:
#             self.consumer.close()
#
#
# if __name__ == "__main__":
#     utils.load_env()
#     logging_config.configure_logging()
#
#     bootstrap_server = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
#     topic = os.environ.get("KAFKA_TOPIC")
#     group_id = os.environ.get("KAFKA_GROUP_ID", "my-consumer-group")
#
#     consumer = ConsumerClass(bootstrap_server, topic, group_id)
#     consumer.consume_messages()

class ConsumerClass:
    def __init__(self, bootstrap_server, topic, group_id):
        self.bootstrap_server = bootstrap_server
        self.topic = topic
        self.group_id = group_id
        self.consumer = Consumer(
            {"bootstrap.servers": bootstrap_server, "group.id": self.group_id}
        )

    def consume_messages(self):

        self.consumer.subscribe([self.topic])
        # logging.info(f"Successfully subscribed to topic: {self.topic}")
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue

                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    # logging.error(f"Consumer error: {msg.error()}")
                    continue
                byte_message = msg.value()
                print(f"Message consumed in bytes: {byte_message} ")

                decoded_message = byte_message.decode("utf-8")
                print(f"Deserialized Message : {decoded_message} ")

                dict_message = json.loads(decoded_message)
                print(dict_message, type(dict_message))

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

if __name__ == "__main__":
    bootstrap_servers = "localhost:19092"
    topic = "test-topic"
    group_id="my-group-id"

    consumer=ConsumerClass(bootstrap_servers, topic, group_id)
    consumer.consume_messages()
