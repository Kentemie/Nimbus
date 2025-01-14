from pydantic import BaseModel


class V1Config(BaseModel):
    PREFIX: str = "/v1"
    AUTH: str = "/auth"
    USERS: str = "/users"
    ROLES: str = "/roles"
    ORDERS: str = "/orders"
    PRODUCTS: str = "/products"


class ApiConfig(BaseModel):
    PREFIX: str = "/api"
    V1: V1Config = V1Config()

    @property
    def BEARER_TOKEN_URL(self) -> str:
        parts = (self.PREFIX, self.V1.PREFIX, self.V1.AUTH, "/login")
        path = "".join(parts)
        return path.removeprefix("/")
