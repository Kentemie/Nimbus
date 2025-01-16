from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IntegerIDMixin, TimestampMixin

if TYPE_CHECKING:
    from .order import Order
    from .role import Role


class User(IntegerIDMixin, TimestampMixin, Base):
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    roles: Mapped[list["Role"]] = relationship(
        argument="Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )

    orders: Mapped[list["Order"]] = relationship(
        argument="Order",
        back_populates="user",
    )

    def get_role_names(self) -> list[str]:
        return [role.name for role in self.roles]
