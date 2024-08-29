# from flask import Flask, request, jsonify
# from confluent_kafka import Producer, Consumer
# import json
# import threading
#
# app = Flask(__name__)
#
# bootstrap_servers = "localhost:19092"
# request_topic = "request-topic"
# response_topic = "response-topic"
# group_id = "consumer-group"
#
# # Kafka producer setup
# producer = Producer({"bootstrap.servers": bootstrap_servers})
#
# # Kafka consumer setup
# consumer = Consumer({
#     "bootstrap.servers": bootstrap_servers,
#     "group.id": group_id,
#     "auto.offset.reset": "earliest"
# })
#
# # Global variable to store the correlation ID for response matching
# pending_responses = {}
#
# # Helper function to send a message to Kafka
# def send_to_kafka(topic, message):
#     json_message = json.dumps(message).encode('utf-8')
#     producer.produce(topic, json_message)
#     producer.flush()
#
# @app.route('/send_request', methods=['POST'])
# def send_request():
#     try:
#         data = request.json
#         correlation_id = str(data.get("device_id", "unknown"))
#
#         # Publish request to Kafka
#         send_to_kafka(request_topic, {"correlation_id": correlation_id, **data})
#
#         # Wait for the response
#         response = wait_for_response(correlation_id)
#
#         return jsonify(response), 200
#     except Exception as e:
#         return jsonify({"error": f"An error occurred: {e}"}), 500
#
# def wait_for_response(correlation_id):
#     """Blocking call to wait for response from Kafka."""
#     import time
#     timeout = 10  # seconds
#     start_time = time.time()
#     while time.time() - start_time < timeout:
#         if correlation_id in pending_responses:
#             return pending_responses.pop(correlation_id)
#         time.sleep(1)
#     return {"error": "Response timeout"}
#
# def process_request():
#     """Thread for consuming requests and producing responses."""
#     while True:
#         msg = consumer.poll(1.0)
#         if msg is None:
#             continue
#         if msg.error():
#             print(f"Consumer error: {msg.error()}")
#             continue
#
#         byte_message = msg.value()
#         decoded_message = byte_message.decode("utf-8")
#         request_data = json.loads(decoded_message)
#         correlation_id = request_data.get("correlation_id")
#
#         # Dummy classification logic
#         classification = "safe" if request_data.get("request_data") == "example_request" else "unsafe"
#
#         response = {
#             "device_id": request_data["device_id"],
#             "classification": classification
#         }
#
#         # Publish response to Kafka
#         send_to_kafka(response_topic, {"correlation_id": correlation_id, **response})
#
#         # Store response in global variable for matching
#         pending_responses[correlation_id] = response
#
# if __name__ == "__main__":
#     consumer.subscribe([request_topic])
#     # Start a thread for processing requests
#     threading.Thread(target=process_request, daemon=True).start()
#     app.run(debug=True, host="0.0.0.0", port=5001)

from flask import Flask, request, jsonify
from confluent_kafka import Producer, Consumer
import json
import threading

import pickle
import numpy as np

app = Flask(__name__)

bootstrap_servers = "localhost:19092"
request_topic = "request-topic"
response_topic = "response-topic"
group_id = "consumer-group"

# Kafka producer setup
producer = Producer({"bootstrap.servers": bootstrap_servers})

# Kafka consumer setup
consumer = Consumer({
    "bootstrap.servers": bootstrap_servers,
    "group.id": group_id,
    "auto.offset.reset": "earliest"
})

# Global variable to store the correlation ID for response matching
pending_responses = {}

# Helper function to send a message to Kafka
def send_to_kafka(topic, message):
    json_message = json.dumps(message).encode('utf-8')
    producer.produce(topic, json_message)
    producer.flush()

@app.route('/send_request', methods=['POST'])
def send_request():
    try:
        data = request.json
        correlation_id = str(data.get("device_id", "unknown"))

        # Publish request to Kafka
        send_to_kafka(request_topic, {"correlation_id": correlation_id, **data})

        # Wait for the response
        response = wait_for_response(correlation_id)

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

def wait_for_response(correlation_id):
    """Blocking call to wait for response from Kafka."""
    import time
    timeout = 10  # seconds
    start_time = time.time()
    while time.time() - start_time < timeout:
        if correlation_id in pending_responses:
            return pending_responses.pop(correlation_id)
        time.sleep(1)
    return {"error": "Response timeout"}

def process_request():
    """Thread for consuming requests and producing responses."""
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        byte_message = msg.value()
        decoded_message = byte_message.decode("utf-8")
        request_data = json.loads(decoded_message)
        correlation_id = request_data.get("correlation_id")

        # Dummy classification logic
        classification = "safe" if request_data.get("request_data") == "example_request" else "unsafe"
        print("classification : "+classification)

        response = {
            "device_id": request_data["device_id"],
            "classification": classification
        }

        # Publish response to Kafka
        send_to_kafka(response_topic, {"correlation_id": correlation_id, **response})

        # Store response in global variable for matching
        pending_responses[correlation_id] = response
        # print("pending_response : " + pending_responses[correlation_id])

if __name__ == "__main__":
    consumer.subscribe([request_topic])
    # Start a thread for processing requests
    threading.Thread(target=process_request, daemon=True).start()
    app.run(debug=True, host="0.0.0.0", port=5001)