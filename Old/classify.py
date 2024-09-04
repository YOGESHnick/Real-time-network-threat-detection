from flask import Flask, request, jsonify
from confluent_kafka import Producer, Consumer
import json
import threading
import logging
import pickle
import numpy as np

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    try:
        json_message = json.dumps(message).encode('utf-8')
        producer.produce(topic, json_message)
        producer.flush()
        logger.info(f"Sent to Kafka topic {topic}: {message}")
    except Exception as e:
        logger.error(f"Failed to send message to Kafka: {e}")

@app.route('/classify', methods=['POST'])
def classify():
    """Dummy classification logic."""
    # request_data = request.json
    request_data = request.get_json()
    # modifying from here:
    model = pickle.load(open('model.pkl', 'rb'))

    sample_values = [
        32.011598, 9.000000, 5.000000, 3.000000, 3.000000, 0.281148, 0.156193, 0.437341, 0.555556, 296.000000,
        32.000000, 40.000000, 168.000000, 32.000000, 40.000000, 0.000000, 2.000000, 1.000000, 3.000000, 3.000000,
        13.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 33.000000, 76.000000, 8.444444, 13.115936,
        0.000000, 23.000000, 32.000000, 6.400000, 9.555103, 0.000000, 33.000000, 108.000000, 7.714286, 11.618477,
        0.000000, 0.000000, 0.000000, 0.000000, 64240.000000, 26847.000000, 502.000000
    ]

    sample_values = np.array(sample_values).reshape(1, -1)
    prediction = model.predict(sample_values)
    print(prediction)

    # old code from here line 46-here are new
    classification = "safe" if request_data.get("request_data") == "example_request" else "unsafe"
    # return jsonify({"classification": classification})
    return jsonify({"classification": classification , "prediciton": prediction[0]})

def process_request():
    """Thread for consuming requests and producing responses."""
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logger.error(f"Consumer error: {msg.error()}")
            continue

        byte_message = msg.value()
        decoded_message = byte_message.decode("utf-8")
        request_data = json.loads(decoded_message)
        correlation_id = request_data.get("correlation_id")

        # Dummy classification logic
        classification = classify().json.get("classification")
        logger.info(f"Classification: {classification}")

        response = {
            "device_id": request_data["device_id"],
            "classification": classification
        }

        # Publish response to Kafka
        send_to_kafka(response_topic, {"correlation_id": correlation_id, **response})

        # Store response in global variable for matching
        pending_responses[correlation_id] = response
        logger.info(f"Pending response: {pending_responses[correlation_id]}")

if __name__ == "__main__":
    consumer.subscribe([request_topic])
    # Start a thread for processing requests
    threading.Thread(target=process_request, daemon=True).start()
    app.run(debug=True, host="0.0.0.0", port=5002)