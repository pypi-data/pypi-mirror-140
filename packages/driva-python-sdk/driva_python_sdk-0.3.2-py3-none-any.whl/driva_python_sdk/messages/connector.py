"""Module for classes for creating Kafka Sink Connectors."""
from typing import Dict
from typing import Union

import requests
from pydantic import BaseModel

ConnectorConfig = Dict[str, Union[str, bool, int]]


class BaseConnector(BaseModel):
    """Base class for all Kafka connector configurations."""

    name: str
    topics: str
    key_converter: str = "org.apache.kafka.connect.storage.StringConverter"
    transforms: str = "removenullfields"
    transforms_removenullfields_type: str = (
        "us.anant.kafka.connect.smt.RemoveNullFields$Value"
    )

    def _generate_config(self) -> ConnectorConfig:
        config: ConnectorConfig = {}
        for k, v in self.dict().items():
            if k == "name":
                continue
            new_k = k.replace("_", ".")
            config[new_k] = v
        return config

    def create_connector(self) -> None:
        """Creates the Kafka Connector.

        If it already exists updates the configuration.
        """
        url = f"http://localhost:8083/connectors/{self.name}/config"
        config = self._generate_config()
        headers = {"content-type": "application/json"}
        res = requests.put(url=url, json=config, headers=headers)

        if res.status_code > 201:
            raise ValueError(
                f"""
                Failed to create connector with code {res.status_code}.
                Details: {res.json()}
                """
            )


class ElasticConnector(BaseConnector):
    """Configuration for Elasticsearch connector.

    More details at
    https://docs.confluent.io/kafka-connect-elasticsearch/current/configuration_options.html#elasticsearch-overview-config
    """

    username: str
    password: str
    connection_url: str
    connector_class: str = (
        "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector"
    )
    type_name: str = "_doc"
    schema_ignore: bool = False
    key_ignore: bool = False
    behavior_on_null_values: str = "delete"
    behavior_on_malformed_documents: str = "ignore"
    write_method: str = "upsert"


class PostgresConnector(BaseConnector):
    """Configuration for Postgres connector.

    More details at
    https://docs.confluent.io/kafka-connect-jdbc/current/sink-connector/sink_config_options.html#sink-config-options
    """

    connection_user: str
    connection_password: str
    connection_url: str
    pk_fields: str
    connector_class: str = "io.confluent.connect.jdbc.JdbcSinkConnector"
    # connector_class: str = (
    #     "no.norsktipping.kafka.connect.jdbc.connector.JdbcSinkConnector_Flatten"
    # )
    auto_create: bool = True
    auto_evolve: bool = True
    pk_mode: str = "record_key"
    insert_mode: str = "upsert"
    delete_enabled: bool = True
    transforms: str = "dropsome,removenullfields"
    transforms_dropsome_blacklist: str = ""
    transforms_dropsome_type: str = (
        "org.apache.kafka.connect.transforms.ReplaceField$Value"
    )


class MongoConnector(BaseConnector):
    """Configuration for MongoDB connector.

    More details at
    https://docs.mongodb.com/kafka-connector/current/sink-connector/configuration-properties/#std-label-kafka-sink-configuration-properties
    """

    database: str
    collection: str
    connection_uri: str
    connector_class: str = "com.mongodb.kafka.connect.MongoSinkConnector"
    mongodb_delete_on_null_values: bool = True
    delete_on_null_values: bool = True
    document_id_strategy_overwrite_existing: bool = True
    document_id_strategy: str = (
        "com.mongodb.kafka.connect.sink.processor.id.strategy.ProvidedInKeyStrategy"
    )
    transforms: str = "hk,removenullfields"
    transforms_hk_type: str = "org.apache.kafka.connect.transforms.HoistField$Key"
    transforms_hk_field: str = "_id"
    writemodel_strategy: str = (
        "com.mongodb.kafka.connect.sink.writemodel.strategy.UpdateOneTimestampsStrategy"
    )
