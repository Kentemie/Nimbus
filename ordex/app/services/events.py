from core.infrastructure import kafka_manager


async def send_order_status_update_event(
    order_id: int,
    old_status: str,
    new_status: str,
):
    message = {
        "order_id": order_id,
        "old_status": old_status,
        "new_status": new_status,
    }

    await kafka_manager.send(value=message)
