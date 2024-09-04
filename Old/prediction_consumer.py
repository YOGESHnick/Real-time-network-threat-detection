# from confluent_kafka import Consumer
# import json
# import logging
#
# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# # Kafka configuration
# bootstrap_servers = "localhost:19092"
# classification_topic = "classification-topic"
# group_id = "consumer-group"
#
# # Kafka consumer setup
# consumer = Consumer({
#     "bootstrap.servers": bootstrap_servers,
#     "group.id": group_id,
#     "auto.offset.reset": "earliest"
# })
#
# consumer.subscribe([classification_topic])
#
#
# def consume_messages():
#     """Continuously consume messages from Kafka topic and print them."""
#     logger.info("Starting to consume messages from Kafka topic: %s", classification_topic)
#     while True:
#         msg = consumer.poll(timeout=1.0)
#         if msg is None:
#             continue
#         if msg.error():
#             logger.error(f"Consumer error: {msg.error()}")
#             continue
#
#         byte_message = msg.value()
#         decoded_message = byte_message.decode("utf-8")
#         response_data = json.loads(decoded_message)
#
#         logger.info(f"Received message: {response_data}")
#
#
# if __name__ == "__main__":
#     consume_messages()


# from confluent_kafka import Consumer
# import json
# import logging
#
# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# # Kafka configuration
# bootstrap_servers = "localhost:19092"
# classification_topic = "classification-topic"
# group_id = "consumer-group"
#
# # Kafka consumer setup
# consumer = Consumer({
#     "bootstrap.servers": bootstrap_servers,
#     "group.id": group_id,
#     "auto.offset.reset": "earliest"
# })
#
# consumer.subscribe([classification_topic])
#
#
# def consume_messages():
#     """Continuously consume messages from Kafka topic and print them."""
#     logger.info("Starting to consume messages from Kafka topic: %s", classification_topic)
#     while True:
#         msg = consumer.poll(timeout=1.0)
#         if msg is None:
#             continue
#         if msg.error():
#             logger.error(f"Consumer error: {msg.error()}")
#             continue
#
#         # Decode the message value
#         byte_message = msg.value()
#         if byte_message is not None:
#             try:
#                 decoded_message = byte_message.decode("utf-8")
#                 logger.info(f"Received message: {decoded_message}")
#
#                 # Parse the JSON message
#                 response_data = json.loads(decoded_message)
#                 logger.info(f"Parsed JSON message: {response_data}")
#             except json.JSONDecodeError as e:
#                 logger.error(f"Failed to decode JSON message: {e}")
#             except Exception as e:
#                 logger.error(f"An unexpected error occurred: {e}")
#
#
# if __name__ == "__main__":
#     consume_messages()


#  C M D    A T T E M P T    1


# import subprocess
#
# def consume_kafka_topic():
#     # Command to execute the Docker command to consume messages from the Kafka topic
#     cmd = ["docker", "exec", "-it", "redpanda", "rpk", "topic", "consume", "classification-topic"]
#
#     # Use subprocess to run the command and continuously listen for new data
#     process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#
#     try:
#         while True:
#             # Read the output line by line
#             output = process.stdout.readline()
#             if output:
#                 print(f"New Data: {output.strip()}")
#             if process.poll() is not None:
#                 break
#     except KeyboardInterrupt:
#         print("Stopped consuming messages.")
#     finally:
#         process.terminate()
#
# if __name__ == "__main__":
#     consume_kafka_topic()

#  A T T E M P T  2   ------------------------------ W O R K I N G ------------------------------

# import subprocess
# import json
#
# def consume_latest_kafka_message():
#     # Command to consume messages starting from the latest offset
#     cmd = [
#         "docker", "exec", "-i", "redpanda", "rpk", "topic", "consume",
#         "classification-topic", "--offset", "end"
#     ]
#
#     # Use subprocess to run the command and continuously listen for new data
#     process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#
#     try:
#         while True:
#             # Read the output line by line
#             output = process.stdout.readline()
#             if output:
#                 # Print only the latest incoming data
#                 print(f"New Data: {output.strip()}")
#
#
#             # If process ends, exit loop
#             if process.poll() is not None:
#                 break
#     except KeyboardInterrupt:
#         print("Stopped consuming messages.")
#     finally:
#         process.terminate()
#
# if __name__ == "__main__":
#     consume_latest_kafka_message()

 # ------------------------------ W O R K I N G ------------------------------

#  M Y   O W N   A T T E M P T

import json
import logging
from confluent_kafka import Consumer
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logging.info(f"Successfully subscribed to topic: {self.topic}")
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue

                if msg.error():
                    logging.info(f"Consumer error: {msg.error()}")
                    # logging.error(f"Consumer error: {msg.error()}")
                    continue
                byte_message = msg.value()
                # print(f"Message consumed in bytes: {byte_message} ")

                decoded_message = byte_message.decode("utf-8")
                # print(f"Deserialized Message : {decoded_message} ")

                dict_message = json.loads(decoded_message)
                logging.info(dict_message)

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

if __name__ == "__main__":
    bootstrap_servers = "localhost:19092"
    topic = "classification-topic"
    group_id="consumer-group"

    consumer=ConsumerClass(bootstrap_servers, topic, group_id)
    consumer.consume_messages()