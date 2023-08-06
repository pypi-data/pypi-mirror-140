"""Module for the base settings definition."""
from pydantic import BaseModel
from pydantic import BaseSettings


class MessageBrokerSettings(BaseModel):
    """Representation of the settings available for the event bus."""

    broker_host: str = "localhost:9092"
    schema_registry_host: str = "http://localhost:8081"


class Settings(BaseSettings):
    """Representation for the SDK settings."""

    message_broker: MessageBrokerSettings = MessageBrokerSettings()

    class Config:
        """Defines how the this model is configured."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
