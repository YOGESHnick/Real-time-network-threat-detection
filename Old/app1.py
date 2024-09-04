# from flask import Flask, request, jsonify
# from confluent_kafka import Producer, Consumer
# import json
# import threading
# import logging
# import numpy as np
# import pickle
# import logging
#
# # K A F K A    C O N S U M E R    C O D E
# class ConsumerClass:
#     def __init__(self, bootstrap_server, topic, group_id):
#         self.bootstrap_server = bootstrap_server
#         self.topic = topic
#         self.group_id = group_id
#         self.consumer = Consumer(
#             {"bootstrap.servers": bootstrap_server, "group.id": self.group_id}
#         )
#
#     def consume_messages(self):
#
#         self.consumer.subscribe([self.topic])
#         logging.info(f"Successfully subscribed to topic: {self.topic}")
#         try:
#             while True:
#                 msg = self.consumer.poll(1.0)
#                 if msg is None:
#                     continue
#
#                 if msg.error():
#                     logging.info(f"Consumer error: {msg.error()}")
#                     # logging.error(f"Consumer error: {msg.error()}")
#                     continue
#                 byte_message = msg.value()
#                 # print(f"Message consumed in bytes: {byte_message} ")
#
#                 decoded_message = byte_message.decode("utf-8")
#                 # print(f"Deserialized Message : {decoded_message} ")
#
#                 dict_message = json.loads(decoded_message)
#                 logging.info(dict_message)
#
#         except KeyboardInterrupt:
#             pass
#         finally:
#             self.consumer.close()
#
# app = Flask(__name__)
#
# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# bootstrap_servers = "localhost:19092"
# classification_topic = "classification-topic"
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
#     try:
#         json_message = json.dumps(message).encode('utf-8')
#         producer.produce(topic, json_message)
#         producer.flush()
#         logger.info(f"Sent to Kafka topic {topic}: {message}")
#     except Exception as e:
#         logger.error(f"Failed to send message to Kafka: {e}")
#
# @app.route('/getRequest', methods=['POST'])
# def get_request():
#     try:
#         request_data = request.get_json()
#         model = pickle.load(open('model.pkl', 'rb'))
#
#         sample_values = [
#             32.011598, 9.000000, 5.000000, 3.000000, 3.000000, 0.281148, 0.156193, 0.437341, 0.555556, 296.000000,
#             32.000000, 40.000000, 168.000000, 32.000000, 40.000000, 0.000000, 2.000000, 1.000000, 3.000000, 3.000000,
#             13.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 33.000000, 76.000000, 8.444444, 13.115936,
#             0.000000, 23.000000, 32.000000, 6.400000, 9.555103, 0.000000, 33.000000, 108.000000, 7.714286, 11.618477,
#             0.000000, 0.000000, 0.000000, 0.000000, 64240.000000, 26847.000000, 502.000000
#         ]
#
#         extracted_values = [
#             float(request_data.get("flow_duration", 0)),
#             float(request_data.get("fwd_pkts_tot", 0)),
#             float(request_data.get("bwd_pkts_tot", 0)),
#             float(request_data.get("fwd_data_pkts_tot", 0)),
#             float(request_data.get("bwd_data_pkts_tot", 0)),
#             float(request_data.get("fwd_pkts_per_sec", 0)),
#             float(request_data.get("bwd_pkts_per_sec", 0)),
#             float(request_data.get("flow_pkts_per_sec", 0)),
#             float(request_data.get("down_up_ratio", 0)),
#             float(request_data.get("fwd_header_size_tot", 0)),
#             float(request_data.get("fwd_header_size_min", 0)),
#             float(request_data.get("fwd_header_size_max", 0)),
#             float(request_data.get("bwd_header_size_tot", 0)),
#             float(request_data.get("bwd_header_size_min", 0)),
#             float(request_data.get("bwd_header_size_max", 0)),
#             float(request_data.get("flow_FIN_flag_count", 0)),
#             float(request_data.get("flow_SYN_flag_count", 0)),
#             float(request_data.get("flow_RST_flag_count", 0)),
#             float(request_data.get("fwd_PSH_flag_count", 0)),
#             float(request_data.get("bwd_PSH_flag_count", 0)),
#             float(request_data.get("flow_ACK_flag_count", 0)),
#             float(request_data.get("fwd_URG_flag_count", 0)),
#             float(request_data.get("bwd_URG_flag_count", 0)),
#             float(request_data.get("flow_CWR_flag_count", 0)),
#             float(request_data.get("flow_ECE_flag_count", 0)),
#             float(request_data.get("fwd_pkts_payload.min", 0)),
#             float(request_data.get("fwd_pkts_payload.max", 0)),
#             float(request_data.get("fwd_pkts_payload.tot", 0)),
#             float(request_data.get("fwd_pkts_payload.avg", 0)),
#             float(request_data.get("fwd_pkts_payload.std", 0)),
#             float(request_data.get("bwd_pkts_payload.min", 0)),
#             float(request_data.get("bwd_pkts_payload.max", 0)),
#             float(request_data.get("bwd_pkts_payload.tot", 0)),
#             float(request_data.get("bwd_pkts_payload.avg", 0)),
#             float(request_data.get("bwd_pkts_payload.std", 0)),
#             float(request_data.get("flow_pkts_payload.min", 0)),
#             float(request_data.get("flow_pkts_payload.max", 0)),
#             float(request_data.get("flow_pkts_payload.tot", 0)),
#             float(request_data.get("flow_pkts_payload.avg", 0)),
#             float(request_data.get("flow_pkts_payload.std", 0)),
#             float(request_data.get("fwd_bulk_packets", 0)),
#             float(request_data.get("bwd_bulk_packets", 0)),
#             float(request_data.get("fwd_bulk_rate", 0)),
#             float(request_data.get("bwd_bulk_rate", 0)),
#             float(request_data.get("fwd_init_window_size", 0)),
#             float(request_data.get("bwd_init_window_size", 0)),
#             float(request_data.get("fwd_last_window_size", 0))
#         ]
#
#         # sample_values = np.array(sample_values).reshape(1, -1)
#         sample_values = np.array(extracted_values).reshape(1, -1)
#
#         prediction = model.predict(sample_values)
#         print(prediction)
#
#         # classification = "safe" if request_data.get("request_data") == "example_request" else "unsafe"
#         response ={"prediciton": prediction[0]}
#
#         send_to_kafka(classification_topic, {"correlation_id": response})
#
#         return jsonify(response), 200
#     except Exception as e:
#         logger.error(f"An error occurred: {e}")
#         return jsonify({"error": f"An error occurred: {e}"}), 500
#
# def wait_for_response(correlation_id):
#     """Blocking call to wait for response from Kafka."""
#     import time
#     timeout = 10  # seconds
#     start_time = time.time()
#     logger.info(f"Waiting for response with correlation_id: {correlation_id}")
#     while time.time() - start_time < timeout:
#         if correlation_id in pending_responses:
#             response = pending_responses.pop(correlation_id)
#             logger.info(f"Response received: {response}")
#             return response
#         time.sleep(1)
#     logger.warning(f"Response timeout for correlation_id: {correlation_id}")
#     return {"error": "Response timeout"}
#
# def process_responses():
#     """Thread for consuming classification responses."""
#     while True:
#         msg = consumer.poll(1.0)
#         if msg is None:
#             continue
#         if msg.error():
#             logger.error(f"Consumer error: {msg.error()}")
#             continue
#
#         byte_message = msg.value()
#         decoded_message = byte_message.decode("utf-8")
#         response_data = json.loads(decoded_message)
#         correlation_id = response_data.get("correlation_id")
#
#         logger.info(f"Received response from Kafka: {response_data}")
#
#         # Store response in global variable for matching
#         pending_responses[correlation_id] = response_data
#         logger.info(f"Pending response updated: {pending_responses}")
#
# if __name__ == "__main__":
#     consumer.subscribe([classification_topic])
#     # Start a thread for processing responses
#     # K A F K A
#     bootstrap_servers = "localhost:19092"
#     topic = "classification-topic"
#     group_id = "consumer-group"
#
#     consumer = ConsumerClass(bootstrap_servers, topic, group_id)
#     consumer.consume_messages()
#     # K A F K A
#
#     threading.Thread(target=process_responses, daemon=True).start()
#     app.run(debug=True, host="0.0.0.0", port=5001)

from flask import Flask, request, jsonify
from confluent_kafka import Producer, Consumer
import json
import threading
import logging
import numpy as np
import pickle

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

@app.route('/getRequest', methods=['POST'])
def get_request():
    try:
        request_data = request.get_json()
        model = pickle.load(open('model.pkl', 'rb'))

        sample_values = [
            32.011598, 9.000000, 5.000000, 3.000000, 3.000000, 0.281148, 0.156193, 0.437341, 0.555556, 296.000000,
            32.000000, 40.000000, 168.000000, 32.000000, 40.000000, 0.000000, 2.000000, 1.000000, 3.000000, 3.000000,
            13.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 33.000000, 76.000000, 8.444444, 13.115936,
            0.000000, 23.000000, 32.000000, 6.400000, 9.555103, 0.000000, 33.000000, 108.000000, 7.714286, 11.618477,
            0.000000, 0.000000, 0.000000, 0.000000, 64240.000000, 26847.000000, 502.000000
        ]


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

        # sample_values = np.array(sample_values).reshape(1, -1)
        sample_values = np.array(extracted_values).reshape(1, -1)

        prediction = model.predict(sample_values)
        print(prediction)

        # classification = "safe" if request_data.get("request_data") == "example_request" else "unsafe"
        response ={"prediction": prediction[0]}

        send_to_kafka(classification_topic, {"correlation_id": response})

        return jsonify(response), 200
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500

def wait_for_response(correlation_id):
    """Blocking call to wait for response from Kafka."""
    import time
    timeout = 10  # seconds
    start_time = time.time()
    logger.info(f"Waiting for response with correlation_id: {correlation_id}")
    while time.time() - start_time < timeout:
        if correlation_id in pending_responses:
            response = pending_responses.pop(correlation_id)
            logger.info(f"Response received: {response}")
            return response
        time.sleep(1)
    logger.warning(f"Response timeout for correlation_id: {correlation_id}")
    return {"error": "Response timeout"}

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

        # Store response in global variable for matching
        pending_responses[correlation_id] = response_data
        logger.info(f"Pending response updated: {pending_responses}")

if __name__ == "__main__":
    consumer.subscribe([classification_topic])
    # Start a thread for processing responses
    threading.Thread(target=process_responses, daemon=True).start()
    app.run(debug=True, host="0.0.0.0", port=5001)