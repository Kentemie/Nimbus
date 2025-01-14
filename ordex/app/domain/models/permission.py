from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IntegerIDMixin, TimestampMixin

if TYPE_CHECKING:
    from .role import Role


class Permission(IntegerIDMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    roles: Mapped[list["Role"]] = relationship(
        argument="Role",
        secondary="role_permissions",
        back_populates="permissions",
    )
