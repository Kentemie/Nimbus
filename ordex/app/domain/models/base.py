from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

from utils import camel_case_to_snake_case
from core.config import settings


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.DATABASE.NAMING_CONVENTION,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa
        return f"{camel_case_to_snake_case(cls.__name__)}s"
