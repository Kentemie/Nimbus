from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import (
    Float,
    Enum as SqlEnum,
    ForeignKey,
    BIGINT,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped

from .base import Base
from .mixins import IntegerIDMixin, TimestampMixin

from domain.enums import OrderStatus

if TYPE_CHECKING:
    from .user import User
    from .junctions import OrderProduct


class Order(IntegerIDMixin, TimestampMixin, Base):
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SqlEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False
    )
    total_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship("User", back_populates="orders")

    order_products: Mapped[list["OrderProduct"]] = relationship(
        argument="OrderProduct",
        back_populates="order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
