from typing import Optional  # noqa

from pydantic import BaseModel, Field, ConfigDict


class CreateUpdateDictModel(BaseModel):
    def get_create_update_dict(self):
        return self.model_dump(
            exclude_unset=True,
            exclude={
                "id",
            },
        )


class Role(CreateUpdateDictModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Администратор")
    slug: str = Field(..., example="admin")

    model_config = ConfigDict(from_attributes=True)


class RoleCreate(CreateUpdateDictModel):
    name: str = Field(..., example="Пользователь")
    slug: str = Field(..., example="user")


class RoleUpdate(CreateUpdateDictModel):
    name: Optional[str] = Field(None, example="Новый пользователь")
    slug: Optional[str] = Field(None, example="new-user")
