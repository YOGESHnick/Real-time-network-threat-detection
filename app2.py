import threading
from flask import Flask, request, jsonify
from confluent_kafka import Producer, Consumer
import json
import logging
import numpy as np
import pickle
import uuid
import time

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bootstrap_servers = "localhost:19092"
classification_topic = "classification-topic"
group_id = "consumer-group"

# Kafka producer setup
producer = Producer({"bootstrap.servers": bootstrap_servers})

# Kafka consumer setup
consumer = Consumer({
    "bootstrap.servers": bootstrap_servers,
    "group.id": group_id,
    "auto.offset.reset": "earliest"
})

# Global dictionary to store the correlation ID for response matching
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

@app.route('/getRequest', methods=['POST'])
def get_request():
    try:
        request_data = request.get_json()

        # Generate a unique correlation ID
        correlation_id = str(uuid.uuid4())

        # Extract all the features from the request
        extracted_values = [
            float(request_data.get("flow_duration", 0)),
            float(request_data.get("fwd_pkts_tot", 0)),
            float(request_data.get("bwd_pkts_tot", 0)),
            float(request_data.get("fwd_data_pkts_tot", 0)),
            float(request_data.get("bwd_data_pkts_tot", 0)),
            float(request_data.get("fwd_pkts_per_sec", 0)),
            float(request_data.get("bwd_pkts_per_sec", 0)),
            float(request_data.get("flow_pkts_per_sec", 0)),
            float(request_data.get("down_up_ratio", 0)),
            float(request_data.get("fwd_header_size_tot", 0)),
            float(request_data.get("fwd_header_size_min", 0)),
            float(request_data.get("fwd_header_size_max", 0)),
            float(request_data.get("bwd_header_size_tot", 0)),
            float(request_data.get("bwd_header_size_min", 0)),
            float(request_data.get("bwd_header_size_max", 0)),
            float(request_data.get("flow_FIN_flag_count", 0)),
            float(request_data.get("flow_SYN_flag_count", 0)),
            float(request_data.get("flow_RST_flag_count", 0)),
            float(request_data.get("fwd_PSH_flag_count", 0)),
            float(request_data.get("bwd_PSH_flag_count", 0)),
            float(request_data.get("flow_ACK_flag_count", 0)),
            float(request_data.get("fwd_URG_flag_count", 0)),
            float(request_data.get("bwd_URG_flag_count", 0)),
            float(request_data.get("flow_CWR_flag_count", 0)),
            float(request_data.get("flow_ECE_flag_count", 0)),
            float(request_data.get("fwd_pkts_payload.min", 0)),
            float(request_data.get("fwd_pkts_payload.max", 0)),
            float(request_data.get("fwd_pkts_payload.tot", 0)),
            float(request_data.get("fwd_pkts_payload.avg", 0)),
            float(request_data.get("fwd_pkts_payload.std", 0)),
            float(request_data.get("bwd_pkts_payload.min", 0)),
            float(request_data.get("bwd_pkts_payload.max", 0)),
            float(request_data.get("bwd_pkts_payload.tot", 0)),
            float(request_data.get("bwd_pkts_payload.avg", 0)),
            float(request_data.get("bwd_pkts_payload.std", 0)),
            float(request_data.get("flow_pkts_payload.min", 0)),
            float(request_data.get("flow_pkts_payload.max", 0)),
            float(request_data.get("flow_pkts_payload.tot", 0)),
            float(request_data.get("flow_pkts_payload.avg", 0)),
            float(request_data.get("flow_pkts_payload.std", 0)),
            float(request_data.get("fwd_bulk_packets", 0)),
            float(request_data.get("bwd_bulk_packets", 0)),
            float(request_data.get("fwd_bulk_rate", 0)),
            float(request_data.get("bwd_bulk_rate", 0)),
            float(request_data.get("fwd_init_window_size", 0)),
            float(request_data.get("bwd_init_window_size", 0)),
            float(request_data.get("fwd_last_window_size", 0))
        ]

        # Ensure the number of features matches what the model expects
        if len(extracted_values) != 47:
            raise ValueError("Incorrect number of features provided. Expected 47.")

        # Convert the list to a numpy array and reshape it for model input
        sample_values = np.array(extracted_values).reshape(1, -1)

        # Load the model and make a prediction
        # model = pickle.load(open('model.pkl', 'rb'))
        model = pickle.load(open('RandomForestModel.pkl', 'rb'))
        prediction = model.predict(sample_values)

        unsafe_predictions = [
            'ARP_poisioning', 'DDOS_Slowloris', 'DOS_SYN_Hping', 'MQTT_Publish',
            'Metasploit_Brute_Force_SSH', 'NMAP_FIN_SCAN', 'NMAP_OS_DETECTION',
            'NMAP_TCP_scan', 'NMAP_UDP_SCAN', 'NMAP_XMAS_TREE_SCAN',
            'Thing_Speak', 'Wipro_bulb'
        ]

        # Check if the prediction is in the safe list
        if prediction[0] in unsafe_predictions:
            security = "safe"
        else:
            security = "unsafe"

        # Create an Event object for synchronization
        response_event = threading.Event()

        # Store the event in the global dictionary
        pending_responses[correlation_id] = {"event": response_event, "data": None}

        # Prepare the message to be sent to Kafka
        message = {
            "correlation_id": correlation_id,
            "prediction": prediction[0],
            "security":security
        }
        send_to_kafka(classification_topic, message)

        # Wait for the Kafka response
        response_received = response_event.wait(timeout=10)  # wait for up to 10 seconds

        if response_received:
            # Retrieve the response data
            response = pending_responses.pop(correlation_id)["data"]
            return jsonify(response), 200
        else:
            logger.warning(f"Response timeout for correlation_id: {correlation_id}")
            pending_responses.pop(correlation_id, None)  # Clean up on timeout
            return jsonify({"error": "Response timeout"}), 500

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500


def process_responses():
    """Thread for consuming classification responses."""
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logger.error(f"Consumer error: {msg.error()}")
            continue

        byte_message = msg.value()
        decoded_message = byte_message.decode("utf-8")
        response_data = json.loads(decoded_message)
        correlation_id = response_data.get("correlation_id")

        logger.info(f"Received response from Kafka: {response_data}")

        # Retrieve the event from the global dictionary
        if correlation_id in pending_responses:
            pending_responses[correlation_id]["data"] = response_data
            pending_responses[correlation_id]["event"].set()  # Signal the event
        else:
            logger.warning(f"Received response for unknown correlation_id: {correlation_id}")


if __name__ == "__main__":
    consumer.subscribe([classification_topic])
    # Start a thread for processing responses
    threading.Thread(target=process_responses, daemon=True).start()
    app.run(debug=True, host="0.0.0.0", port=5001)