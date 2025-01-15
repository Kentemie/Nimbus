from pydantic import BaseModel


class KafkaConfig(BaseModel):
    BOOTSTRAP_SERVERS: str | list[str]
    TOPIC: str
