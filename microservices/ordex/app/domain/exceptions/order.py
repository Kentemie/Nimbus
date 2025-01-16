from .common import NimbusException


class OrderException(NimbusException):
    """Базовый класс для исключений, связанных с заказами."""

    pass


class OrderIsConfirmedException(OrderException):
    def __init__(self, order_id: int = None):
        message = (
            f"Заказ с ID {order_id} уже подтверждён и не может быть изменён."
            if order_id
            else "Заказ уже подтверждён и не может быть изменён."
        )
        super().__init__(message, details={"order_id": order_id})
