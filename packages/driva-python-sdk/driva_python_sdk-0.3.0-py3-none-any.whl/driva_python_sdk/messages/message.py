"""Module for Message base definition."""
from pydantic_avro.base import AvroBase  # type: ignore


class Message(AvroBase):  # type: ignore
    """Base model for events sent/received by clients."""

    def get_key(self) -> bytes:
        """Returns the message key to used by Kafka."""
        raise NotImplementedError("Please implement the method get_key")
