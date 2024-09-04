from confluent_kafka import Producer
from producer import ProducerClass
from admin import Admin
import json
import jsonschema

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

class User:
    def __init__(self, first_name, middle_name, last_name, age):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.age = age

def user_to_dict(user):
    """Return a dictionary representation of a User instance for serialization."""
    return {
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "age": user.age,
    }

class JSONProducerClass(ProducerClass):
    def __init__(self, bootstrap_server, topic, schema):
        super().__init__(bootstrap_server, topic)
        self.schema = schema
        self.bootstrap_server = bootstrap_server
        self.topic = topic
        # self.topic = "classification-topic"
        self.value_serializer = lambda v: json.dumps(v).encode('utf-8')
        # self.producer = Producer({'bootstrap.servers': self.bootstrap_server})

    def send_message(self, message):
        try:
            # Validate the message against the schema

            # jsonschema.validate(instance=message, schema=self.schema)
            jsonschema.validate(message, self.schema)
            json_message = self.value_serializer(message)
            self.producer.produce(self.topic, json_message)
            # self.producer.flush()
            print("Message sent successfully")
        except jsonschema.ValidationError as ve:
            print(f"Schema validation error: {ve.message}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    bootstrap_servers = "localhost:19092"
    topic = "test-topic"
    a = Admin(bootstrap_servers)
    a.create_topic(topic)
    producer = JSONProducerClass(bootstrap_servers, topic, schema)

    try:
        while True:
            first_name = input("Enter your first name: ")
            middle_name = input("Enter your middle name: ")
            last_name = input("Enter your last name: ")
            age = int(input("Enter your age: "))

            user = User(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                age=age,
            )
            producer.send_message(user_to_dict(user))
    except KeyboardInterrupt:
        pass
    finally:
        producer.producer.flush()
