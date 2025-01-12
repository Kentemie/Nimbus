from pydantic import BaseModel


class V1Config(BaseModel):
    PREFIX: str = "/v1"
    USERS: str = "/users"


class ApiConfig(BaseModel):
    PREFIX: str = "/api"
