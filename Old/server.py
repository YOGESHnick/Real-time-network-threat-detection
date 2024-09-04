from flask import Flask, request, jsonify
from confluent_kafka import Producer, Consumer, KafkaError
import json
import jsonschema

app = Flask(__name__)

# Define the Kafka topic, bootstrap server, and schema
bootstrap_servers = "localhost:19092"
topic = "test-topic"
group_id = "my-group-id"

schema = {
    "type": "object",
    "properties": {
        "first_name": {"type": "string"},
        "middle_name": {"type": "string"},
        "last_name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0},
    },
    "required": ["first_name", "last_name", "age"],
    "additionalProperties": False,
}

# Set up the Kafka producer
producer = Producer({"bootstrap.servers": bootstrap_servers})

# Set up the Kafka consumer
consumer = Consumer({
    "bootstrap.servers": bootstrap_servers,
    "group.id": group_id,
    "auto.offset.reset": "earliest"
})
consumer.subscribe([topic])

@app.route('/send', methods=['POST'])
def send_to_kafka():
    try:
        data = request.json

        # Validate the incoming JSON data against the schema
        jsonschema.validate(data, schema)

        # Serialize the data to JSON and send it to Kafka
        json_message = json.dumps(data).encode('utf-8')
        producer.produce(topic, json_message)
        producer.flush()

        return jsonify({"status": "Message sent successfully"}), 200
    except jsonschema.ValidationError as ve:
        return jsonify({"error": f"Schema validation error: {ve.message}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/consume', methods=['GET'])
def consume_from_kafka():
    try:
        # Poll for messages from Kafka
        msg = consumer.poll(5.0)
        if msg is None:
            return jsonify({"status": "No message received"}), 200

        if msg.error():
            return jsonify({"error": f"Consumer error: {msg.error()}"}), 500

        # Decode and deserialize the message
        byte_message = msg.value()
        decoded_message = byte_message.decode("utf-8")
        dict_message = json.loads(decoded_message)

        # Here you can process the message and respond as needed
        # In this case, we're just returning "hi"
        return jsonify({"message": "hi", "data": dict_message}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8898)
