"""Module for the Message Broker abstraction."""
from typing import Generator
from typing import Type
from typing import TypeVar

from kafka.admin import KafkaAdminClient  # type: ignore
from kafka.admin import NewTopic
from kafka.consumer import KafkaConsumer  # type: ignore
from kafka.producer import KafkaProducer  # type: ignore
from schema_registry.client import schema  # type: ignore
from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import AvroMessageSerializer  # type: ignore

from driva_python_sdk.core.settings import Settings
from driva_python_sdk.messages.message import Message


MessageType = TypeVar("MessageType", bound=Message)


class MessageBroker:
    """This is an abstraction to interact with the Kafka Message Broker."""

    def __init__(self) -> None:
        """Initializes the MessageBroker.

        It uses the settings automatically loaded from the environment.
        """
        self.setting = Settings()
        broker_host = self.setting.message_broker.broker_host
        self.kafka_admin_client = KafkaAdminClient(
            bootstrap_servers=[broker_host],
            client_id="admin_client",
        )
        self.kafka_producer = KafkaProducer(bootstrap_servers=[broker_host])
        schema_registry_url = self.setting.message_broker.schema_registry_host
        self.schema_registry_client = SchemaRegistryClient(url=schema_registry_url)
        self.message_serializer = AvroMessageSerializer(self.schema_registry_client)

    def create_topic_with_schema(
        self, cls: Type[Message], num_partitions: int = 1
    ) -> int:
        """Creates a topic with the given schema associated.

        The topic name will be infered from the class name.
        The schema name will be <topic>-value.
        """
        topic_name = cls.__name__.lower()
        subject_name = topic_name + "-value"
        avro_schema = cls.avro_schema()

        schema_id: int = self.schema_registry_client.register(
            subject=subject_name, schema=schema.AvroSchema(avro_schema)
        )
        topic = NewTopic(
            name=topic_name, num_partitions=num_partitions, replication_factor=1
        )
        self.kafka_admin_client.create_topics(new_topics=[topic])

        return schema_id

    def send(self, message: Message) -> None:
        """Send the message to the right topic.

        The name of the topic is infered from the class name.
        """
        topic_name = message.__class__.__name__.lower()
        subject_name = topic_name + "-value"
        avro_schema = message.avro_schema()

        key = message.get_key()
        value = self.message_serializer.encode_record_with_schema(
            subject=subject_name,
            schema=schema.AvroSchema(avro_schema),
            record=message.dict(exclude_none=True, exclude_unset=True),
        )
        self.kafka_producer.send(topic=topic_name, value=value, key=key)
        self.kafka_producer.flush()

    def consume(
        self, cls: Type[MessageType], from_beggining: bool = True
    ) -> Generator[MessageType, None, None]:
        """Consumes messages from the right topic.

        The name of the topic is infered from the class name.
        Raises ValueError if can't deserialize the message.
        """
        topic_name = cls.__name__.lower()
        consumer = KafkaConsumer(
            topic_name, auto_offset_reset="earliest" if from_beggining else "latest"
        )
        for msg in consumer:
            value = self.message_serializer.decode_message(msg.value)
            if value is None:
                raise ValueError("Failed to deserialize message")
            message = cls(**value)
            yield message
