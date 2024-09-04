from quart import Quart, request, jsonify
from confluent_kafka import Producer, Consumer
import json
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Quart(__name__)

bootstrap_servers = "localhost:19092"
request_topic = "request-topic"
response_topic = "response-topic"
group_id = "consumer-group"

producer = Producer({"bootstrap.servers": bootstrap_servers})
consumer = Consumer({
    "bootstrap.servers": bootstrap_servers,
    "group.id": group_id,
    "auto.offset.reset": "earliest"
})

consumer.subscribe([request_topic])
pending_responses = {}

def send_to_kafka(topic, message):
    json_message = json.dumps(message).encode('utf-8')
    producer.produce(topic, json_message)
    producer.flush()
    logging.info(f"Sent message to topic {topic}: {message}")

async def process_request():
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logging.error(f"Consumer error: {msg.error()}")
            continue

        byte_message = msg.value()
        decoded_message = byte_message.decode("utf-8")
        request_data = json.loads(decoded_message)
        correlation_id = request_data.get("correlation_id")

        logging.info(f"Received request data: {request_data}")

        classification = "safe" if request_data.get("request_data") == "example_request" else "unsafe"

        response = {
            "device_id": request_data["device_id"],
            "classification": classification
        }

        send_to_kafka(response_topic, {"correlation_id": correlation_id, **response})
        pending_responses[correlation_id] = response

@app.route('/send_request', methods=['POST'])
async def send_request():
    data = await request.json
    correlation_id = str(data.get("device_id", "unknown"))

    send_to_kafka(request_topic, {"correlation_id": correlation_id, **data})

    timeout = 10
    start_time = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start_time < timeout:
        if correlation_id in pending_responses:
            return jsonify(pending_responses.pop(correlation_id)), 200
        await asyncio.sleep(1)
    return jsonify({"error": "Response timeout"}), 408

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(process_request())
    app.run(debug=True, host="0.0.0.0", port=5002)
