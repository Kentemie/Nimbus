from datetime import datetime

from sqlalchemy import BIGINT, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from utils import utcnow


class IntegerIDMixin:
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=utcnow,
    )
