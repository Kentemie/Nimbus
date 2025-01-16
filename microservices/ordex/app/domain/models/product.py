from typing import TYPE_CHECKING

from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IntegerIDMixin, TimestampMixin

if TYPE_CHECKING:
    from .order import OrderProduct


class Product(IntegerIDMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)

    order_products: Mapped[list["OrderProduct"]] = relationship(
        argument="OrderProduct",
        back_populates="product",
    )
