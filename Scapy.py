# from scapy.all import sniff, IP, TCP
# from flask import Flask, request, jsonify
# from confluent_kafka import Producer, Consumer
# import json
# import logging
# import numpy as np
# import pickle
# import threading
# import uuid
# import time
#
# # Initialize Flask app
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
# # Global dictionary to store the correlation ID for response matching
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
# # Function to capture live network data
# def capture_network_data():
#     # Initialize variables for features
#     total_fwd_pkts = 0
#     total_bwd_pkts = 0
#     total_fwd_data_pkts = 0
#     total_bwd_data_pkts = 0
#     total_fwd_header_size = 0
#     total_bwd_header_size = 0
#     total_fwd_pkts_payload = 0
#     total_bwd_pkts_payload = 0
#
#     # Define a packet handler
#     def packet_handler(packet):
#         nonlocal total_fwd_pkts, total_bwd_pkts, total_fwd_data_pkts, total_bwd_data_pkts
#         nonlocal total_fwd_header_size, total_bwd_header_size, total_fwd_pkts_payload, total_bwd_pkts_payload
#
#         # Check if the packet is IP/TCP
#         if packet.haslayer(IP) and packet.haslayer(TCP):
#             # Forward and backward packet calculation
#             if packet[IP].src == request.remote_addr:
#                 total_fwd_pkts += 1
#                 total_fwd_data_pkts += len(packet[TCP].payload)
#                 total_fwd_header_size += len(packet[IP])
#                 total_fwd_pkts_payload += len(packet[TCP].payload)
#             elif packet[IP].dst == request.remote_addr:
#                 total_bwd_pkts += 1
#                 total_bwd_data_pkts += len(packet[TCP].payload)
#                 total_bwd_header_size += len(packet[IP])
#                 total_bwd_pkts_payload += len(packet[TCP].payload)
#
#     # Capture packets (you might want to adjust the timeout or packet count based on your needs)
#     sniff(prn=packet_handler, timeout=5)
#
#     # Return the captured values as a dictionary
#     return {
#         "fwd_pkts_tot": total_fwd_pkts,
#         "bwd_pkts_tot": total_bwd_pkts,
#         "fwd_data_pkts_tot": total_fwd_data_pkts,
#         "bwd_data_pkts_tot": total_bwd_data_pkts,
#         "fwd_header_size_tot": total_fwd_header_size,
#         "bwd_header_size_tot": total_bwd_header_size,
#         "fwd_pkts_payload_tot": total_fwd_pkts_payload,
#         "bwd_pkts_payload_tot": total_bwd_pkts_payload
#         # Add more features as needed
#     }
#
# @app.route('/getRequest', methods=['POST'])
# def get_request():
#     try:
#         # Capture network data
#         captured_data = capture_network_data()
#
#         # Generate a unique correlation ID
#         correlation_id = str(uuid.uuid4())
#
#         # Add other relevant data here
#         extracted_values = [
#             captured_data.get("fwd_pkts_tot", 0),
#             captured_data.get("bwd_pkts_tot", 0),
#             captured_data.get("fwd_data_pkts_tot", 0),
#             captured_data.get("bwd_data_pkts_tot", 0),
#             captured_data.get("fwd_header_size_tot", 0),
#             captured_data.get("bwd_header_size_tot", 0),
#             captured_data.get("fwd_pkts_payload_tot", 0),
#             captured_data.get("bwd_pkts_payload_tot", 0),
#             # Add other features as required
#         ]
#
#         # Convert the list to a numpy array and reshape it for model input
#         sample_values = np.array(extracted_values).reshape(1, -1)
#
#         # Load the model and make a prediction
#         model = pickle.load(open('model.pkl', 'rb'))
#         prediction = model.predict(sample_values)
#
#         # Create an Event object for synchronization
#         response_event = threading.Event()
#
#         # Store the event in the global dictionary
#         pending_responses[correlation_id] = {"event": response_event, "data": None}
#
#         # Prepare the message to be sent to Kafka
#         message = {
#             "correlation_id": correlation_id,
#             "prediction": prediction[0]
#         }
#         send_to_kafka(classification_topic, message)
#
#         # Wait for the Kafka response
#         response_received = response_event.wait(timeout=10)  # wait for up to 10 seconds
#
#         if response_received:
#             # Retrieve the response data
#             response = pending_responses.pop(correlation_id)["data"]
#             return jsonify(response), 200
#         else:
#             logger.warning(f"Response timeout for correlation_id: {correlation_id}")
#             pending_responses.pop(correlation_id, None)  # Clean up on timeout
#             return jsonify({"error": "Response timeout"}), 500
#
#     except Exception as e:
#         logger.error(f"An error occurred: {e}")
#         return jsonify({"error": f"An error occurred: {e}"}), 500
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
#         # Retrieve the event from the global dictionary
#         if correlation_id in pending_responses:
#             pending_responses[correlation_id]["data"] = response_data
#             pending_responses[correlation_id]["event"].set()  # Signal the event
#         else:
#             logger.warning(f"Received response for unknown correlation_id: {correlation_id}")
#
# if __name__ == "__main__":
#     consumer.subscribe([classification_topic])
#     # Start a thread for processing responses
#     threading.Thread(target=process_responses, daemon=True).start()
#     app.run(debug=True, host="0.0.0.0", port=5003)



















#   S I M P L E    C O D E
# from flask import Flask, jsonify
# from scapy.all import sniff
# from scapy.layers.inet import IP, TCP
# from threading import Thread
# import numpy as np
# import time
#
# app = Flask(__name__)
#
# # Global variable to store packet data
# packets = []
#
#
# # Function to sniff network traffic
# def packet_sniffer():
#     global packets
#     while True:
#         # Capture packets
#         sniffed_packets = sniff(count=100, timeout=5)  # Adjust count and timeout as needed
#         if sniffed_packets:
#             print(f"Captured {len(sniffed_packets)} packets")
#         packets.extend(sniffed_packets)
#         time.sleep(1)  # Add a small delay to avoid high CPU usage
#
#
# # Start the sniffer in a background thread
# sniffer_thread = Thread(target=packet_sniffer)
# sniffer_thread.daemon = True
# sniffer_thread.start()
#
#
# # Function to compute network features from packets
# def compute_network_features(packets):
#     if not packets:
#         return {}
#
#     # Calculate flow duration
#     flow_duration = packets[-1].time - packets[0].time
#
#     # Counts and totals for various packet features
#     fwd_pkts_tot = sum(1 for p in packets if TCP in p and p[TCP].sport < 1024)
#     bwd_pkts_tot = sum(1 for p in packets if TCP in p and p[TCP].dport < 1024)
#     fwd_data_pkts_tot = sum(len(p[TCP].payload) for p in packets if TCP in p and p[TCP].sport < 1024)
#     bwd_data_pkts_tot = sum(len(p[TCP].payload) for p in packets if TCP in p and p[TCP].dport < 1024)
#
#     fwd_pkts_per_sec = fwd_pkts_tot / (flow_duration if flow_duration > 0 else 1)
#     bwd_pkts_per_sec = bwd_pkts_tot / (flow_duration if flow_duration > 0 else 1)
#     flow_pkts_per_sec = (fwd_pkts_tot + bwd_pkts_tot) / (flow_duration if flow_duration > 0 else 1)
#     down_up_ratio = bwd_pkts_tot / (fwd_pkts_tot if fwd_pkts_tot > 0 else 1)
#
#     # Header sizes
#     fwd_header_sizes = [len(p[IP].raw_packet) - len(p[TCP].payload) for p in packets if TCP in p and p[TCP].sport < 1024]
#     bwd_header_sizes = [len(p[IP].raw_packet) - len(p[TCP].payload) for p in packets if TCP in p and p[TCP].dport < 1024]
#
#     fwd_header_size_tot = sum(fwd_header_sizes)
#     fwd_header_size_min = min(fwd_header_sizes) if fwd_header_sizes else 0
#     fwd_header_size_max = max(fwd_header_sizes) if fwd_header_sizes else 0
#
#     bwd_header_size_tot = sum(bwd_header_sizes)
#     bwd_header_size_min = min(bwd_header_sizes) if bwd_header_sizes else 0
#     bwd_header_size_max = max(bwd_header_sizes) if bwd_header_sizes else 0
#
#     # Flags counts
#     fin_flags = sum(1 for p in packets if TCP in p and p[TCP].flags.F)
#     syn_flags = sum(1 for p in packets if TCP in p and p[TCP].flags.S)
#     rst_flags = sum(1 for p in packets if TCP in p and p[TCP].flags.R)
#     psh_flags = sum(1 for p in packets if TCP in p and p[TCP].flags.P)
#     ack_flags = sum(1 for p in packets if TCP in p and p[TCP].flags.A)
#     urg_flags = sum(1 for p in packets if TCP in p and p[TCP].flags.U)
#     cwr_flags = sum(1 for p in packets if TCP in p and p[TCP].flags.C)
#     ece_flags = sum(1 for p in packets if TCP in p and p[TCP].flags.E)
#
#     # Payload sizes
#     fwd_payloads = [len(p[TCP].payload) for p in packets if TCP in p and p[TCP].sport < 1024]
#     bwd_payloads = [len(p[TCP].payload) for p in packets if TCP in p and p[TCP].dport < 1024]
#
#     fwd_pkts_payload_min = min(fwd_payloads) if fwd_payloads else 0
#     fwd_pkts_payload_max = max(fwd_payloads) if fwd_payloads else 0
#     fwd_pkts_payload_tot = sum(fwd_payloads)
#     fwd_pkts_payload_avg = np.mean(fwd_payloads) if fwd_payloads else 0
#     fwd_pkts_payload_std = np.std(fwd_payloads) if fwd_payloads else 0
#
#     bwd_pkts_payload_min = min(bwd_payloads) if bwd_payloads else 0
#     bwd_pkts_payload_max = max(bwd_payloads) if bwd_payloads else 0
#     bwd_pkts_payload_tot = sum(bwd_payloads)
#     bwd_pkts_payload_avg = np.mean(bwd_payloads) if bwd_payloads else 0
#     bwd_pkts_payload_std = np.std(bwd_payloads) if bwd_payloads else 0
#
#     flow_payloads = fwd_payloads + bwd_payloads
#     flow_pkts_payload_min = min(flow_payloads) if flow_payloads else 0
#     flow_pkts_payload_max = max(flow_payloads) if flow_payloads else 0
#     flow_pkts_payload_tot = sum(flow_payloads)
#     flow_pkts_payload_avg = np.mean(flow_payloads) if flow_payloads else 0
#     flow_pkts_payload_std = np.std(flow_payloads) if flow_payloads else 0
#
#     return {
#         "flow_duration": flow_duration,
#         "fwd_pkts_tot": fwd_pkts_tot,
#         "bwd_pkts_tot": bwd_pkts_tot,
#         "fwd_data_pkts_tot": fwd_data_pkts_tot,
#         "bwd_data_pkts_tot": bwd_data_pkts_tot,
#         "fwd_pkts_per_sec": fwd_pkts_per_sec,
#         "bwd_pkts_per_sec": bwd_pkts_per_sec,
#         "flow_pkts_per_sec": flow_pkts_per_sec,
#         "down_up_ratio": down_up_ratio,
#         "fwd_header_size_tot": fwd_header_size_tot,
#         "fwd_header_size_min": fwd_header_size_min,
#         "fwd_header_size_max": fwd_header_size_max,
#         "bwd_header_size_tot": bwd_header_size_tot,
#         "bwd_header_size_min": bwd_header_size_min,
#         "bwd_header_size_max": bwd_header_size_max,
#         "flow_FIN_flag_count": fin_flags,
#         "flow_SYN_flag_count": syn_flags,
#         "flow_RST_flag_count": rst_flags,
#         "fwd_PSH_flag_count": psh_flags,
#         "bwd_PSH_flag_count": psh_flags,
#         "flow_ACK_flag_count": ack_flags,
#         "fwd_URG_flag_count": urg_flags,
#         "bwd_URG_flag_count": urg_flags,
#         "flow_CWR_flag_count": cwr_flags,
#         "flow_ECE_flag_count": ece_flags,
#         "fwd_pkts_payload_min": fwd_pkts_payload_min,
#         "fwd_pkts_payload_max": fwd_pkts_payload_max,
#         "fwd_pkts_payload_tot": fwd_pkts_payload_tot,
#         "fwd_pkts_payload_avg": fwd_pkts_payload_avg,
#         "fwd_pkts_payload_std": fwd_pkts_payload_std,
#         "bwd_pkts_payload_min": bwd_pkts_payload_min,
#         "bwd_pkts_payload_max": bwd_pkts_payload_max,
#         "bwd_pkts_payload_tot": bwd_pkts_payload_tot,
#         "bwd_pkts_payload_avg": bwd_pkts_payload_avg,
#         "bwd_pkts_payload_std": bwd_pkts_payload_std,
#         "flow_pkts_payload_min": flow_pkts_payload_min,
#         "flow_pkts_payload_max": flow_pkts_payload_max,
#         "flow_pkts_payload_tot": flow_pkts_payload_tot,
#         "flow_pkts_payload_avg": flow_pkts_payload_avg,
#         "flow_pkts_payload_std": flow_pkts_payload_std
#     }
#
#
#
# @app.route('/network_features', methods=['GET'])
# def network_features():
#     if not packets:
#         return jsonify({"message": "No packets captured yet. Please wait and try again."}), 404
#
#     features = compute_network_features(packets)
#     return jsonify(features)
#
# if __name__ == '__main__':
#     # Start the sniffer in a background thread
#     sniffer_thread = Thread(target=packet_sniffer)
#     sniffer_thread.daemon = True
#     sniffer_thread.start()
#
#     # Run the Flask app
#     app.run(host='0.0.0.0', port=5003)
