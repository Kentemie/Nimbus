from typing import TYPE_CHECKING, Protocol, Optional

if TYPE_CHECKING:
    from domain.models import User as UserModel
    from domain.schemas import User as UserSchema


class Strategy(Protocol):
    async def write_token(self, user: "UserModel") -> str: ...

    async def read_token(self, token: Optional[str]) -> Optional["UserSchema"]: ...

    async def destroy_token(self, token: str) -> None: ...
