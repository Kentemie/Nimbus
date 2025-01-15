from typing import TYPE_CHECKING

from sqlalchemy import Integer, BIGINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .order import Order
    from .product import Product


class UserRole(Base):
    user_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    role_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )


class RolePermission(Base):
    role_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    permission_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey(
            "permissions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )


class OrderProduct(Base):
    order_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey(
            "orders.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    product_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey(
            "products.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    order: Mapped["Order"] = relationship(
        argument="Order",
        back_populates="order_products",
    )

    product: Mapped["Product"] = relationship(
        argument="Product",
        back_populates="order_products",
        lazy="joined",
    )
