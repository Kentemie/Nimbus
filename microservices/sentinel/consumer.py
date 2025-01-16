import asyncio
from aiokafka import AIOKafkaConsumer
from pathlib import Path
from datetime import datetime

LOGS_DIR = Path("/app/logs")
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "kafka_consumer.log"


async def consume():
    consumer = AIOKafkaConsumer(
        "ordex",
        bootstrap_servers="kafka:9094",
        group_id="my-group-1",
        session_timeout_ms=10000,
        request_timeout_ms=305000,
        auto_offset_reset="earliest",
    )
    await consumer.start()

    try:
        async for msg in consumer:
            # Формируем текст:
            text = (
                f"{datetime.now().isoformat()} "
                f"topic={msg.topic} partition={msg.partition} offset={msg.offset} "
                f"key={msg.key} value={msg.value.decode('utf-8')} timestamp={msg.timestamp}\n"
            )
            # Записываем в файл
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(text)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume())
