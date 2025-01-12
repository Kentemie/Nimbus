from sqlalchemy import String, Boolean, BIGINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IntIdPkMixin, TimestampMixin


class User(IntIdPkMixin, TimestampMixin, Base):
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )


class Role(IntIdPkMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    permissions: Mapped[list["Permission"]] = relationship(
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
    )

    users: Mapped[list["User"]] = relationship(
        secondary="user_roles",
        back_populates="roles",
        lazy="selectin",
    )


class Permission(IntIdPkMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    roles: Mapped[list["Role"]] = relationship(
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
    )


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
