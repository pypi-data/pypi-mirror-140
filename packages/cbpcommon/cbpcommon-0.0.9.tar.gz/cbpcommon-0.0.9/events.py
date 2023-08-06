import datetime
import io
import threading
import time

import avro.io
import avro.schema
from confluent_kafka import Producer, Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic, NewPartitions

from eslogger import Logger


class MessageException(Exception):
    def __init__(self, m):
        super(m)


class EventManager:
    def __init__(self):
        self.adminClient = AdminClient({
            "bootstrap.servers": "127.0.0.1:9092"
        })
        self.producerClient = Producer({
            "bootstrap.servers": "127.0.0.1:9092"
        })
        self.log = Logger('event-manager')

    def create_address(self, address: str):
        if address not in self.adminClient.list_topics().topics:
            fs = self.adminClient.create_topics([NewTopic(address, 1, 1)])
            for topic, f in fs.items():
                try:
                    f.result()  # The result itself is None
                    self.log.info("Topic {} created".format(topic))
                except Exception as e:
                    self.log.error("Failed to create topic {}: {}".format(topic, e))

    def modify_mailbox_size(self, address: str, size: int):
        if address in self.adminClient.list_topics().topics:
            fs = self.adminClient.create_partitions([NewPartitions(address, size)])
            for topic, f in fs.items():
                try:
                    f.result()  # The result itself is None
                    self.log.info("Additional partitions created for topic {}".format(topic))
                except Exception as e:
                    self.log.error("Failed to add partitions to topic {}: {}".format(topic, e))
            return fs

    def delete_address(self, address: str):
        if address not in self.adminClient.list_topics().topics:
            self.log.warning(f"Address {address} was not found")
            return
        fs = self.adminClient.delete_topics([address])
        # Wait for operation to finish.
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                self.log.info("Topic {} deleted".format(topic))
            except Exception as e:
                self.log.error("Failed to delete topic {}: {}".format(topic, e))

    @staticmethod
    def send_command_to_address(address: str, schema_str: str, command_object: object):
        record_schema = avro.schema.parse(schema_str)
        conf = {'bootstrap.servers': "127.0.0.1:9092"}

        producer = Producer(**conf)

        try:
            writer = avro.io.DatumWriter(record_schema)
            bytes_writer = io.BytesIO()
            encoder = avro.io.BinaryEncoder(bytes_writer)
            writer.write(command_object, encoder)
            raw_bytes = bytes_writer.getvalue()
            producer.produce(address, raw_bytes)
            producer.flush()
        except ValueError:
            print(f"Error Invalid input {command_object}, discarding record...")

    def wait_for_command(self, address: str, schema_str: str, on):

        conf = {'bootstrap.servers': "127.0.0.1:9092",
                'group.id': 'command.query',
                'default.topic.config': {'auto.offset.reset': 'smallest'}}

        consumer = Consumer(**conf)
        consumer.subscribe([address])

        schema = avro.schema.parse(schema_str)

        try:
            while True:
                msg = consumer.poll()
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        self.log.error('ERROR: %% %s [%d] reached end at offset %d\n' %
                                       (msg.topic(), msg.partition(),
                                        msg.offset()))
                    elif msg.error():
                        self.log.error(f"ERROR: {msg.error()}")
                else:
                    message = msg.value()
                    bytes_reader = io.BytesIO(message)
                    decoder = avro.io.BinaryDecoder(bytes_reader)
                    reader = avro.io.DatumReader(schema)
                    try:
                        decoded_msg = reader.read(decoder)
                        on(decoded_msg)
                        # x = threading.Thread(target=on, args=(decoded_msg,))
                        # x.start()
                    except AssertionError as e:
                        self.log.error(f"ERROR: {e}")

        except Exception as e:
            self.log.error(f"Stopped polling for address {address}. Error: {e}")


if __name__ == "__main__":
    em = EventManager()
    em.create_address('unit-test')
    em.modify_mailbox_size('unit-test', 3)
    schema = """
    {
        "namespace": "confluent.io.examples.serialization.avro",
        "name": "Test",
        "type": "record",
        "fields": [
            {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
            {"name": "name", "type": "string"},
            {"name": "value", "type": "string"}            
        ]
    }
    """


    def send_commands():
        count = 0
        while count < 10:
            em.send_command_to_address('unit-test', schema, {
                "timestamp": int(datetime.datetime.timestamp(datetime.datetime.now())),
                "name": "Test",
                "value": str(datetime.datetime.now())})
            time.sleep(10)
            count += 1



    x = threading.Thread(target=send_commands)
    x.start()


    def handler(obj):
        print(datetime.datetime.timestamp(datetime.datetime.now()))
        print(obj['timestamp'])
        print(f"{datetime.datetime.now()}: {obj}")


    y = threading.Thread(target=em.wait_for_command, args=('unit-test', schema, handler,))
    y.start()

    time.sleep(100)

    em.delete_address("unit-test")
