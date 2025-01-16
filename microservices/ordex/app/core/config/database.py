from pydantic import (
    BaseModel,
    computed_field,
    PostgresDsn,
)


class DatabaseConfig(BaseModel):
    NAME: str
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str

    POOL_SIZE: int
    MAX_OVERFLOW: int

    NAMING_CONVENTION: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @computed_field
    @property
    def URL(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            port=self.PORT,
            path=self.NAME,
        )
