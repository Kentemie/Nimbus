import json

from aiokafka import AIOKafkaProducer


class KafkaManager:
    def __init__(
        self,
        bootstrap_servers: str | list[str] = "localhost:9092",
        topic: str = "ordex",
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._producer: AIOKafkaProducer | None = None

    async def start(self):
        # Создаём и запускаем асинхронного продюсера
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self._producer.start()

    async def send_order_status_event(
        self, order_id: int, old_status: str, new_status: str
    ):
        """
        Асинхронно отправляет сообщение в топик ordex о смене статуса заказа.
        """
        if not self._producer:
            raise RuntimeError(
                "Producer is not started. Call start() before sending messages."
            )

        message = {
            "order_id": order_id,
            "old_status": old_status,
            "new_status": new_status,
        }

        await self._producer.send_and_wait(self._topic, value=message)

    async def stop(self):
        if self._producer:
            await self._producer.stop()
