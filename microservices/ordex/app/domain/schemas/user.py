from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from .role import Role


class CreateUpdateDictModel(BaseModel):
    def get_create_update_dict(self):
        return self.model_dump(
            exclude_unset=True,
            exclude={
                "id",
                "is_active",
                "is_verified",
            },
        )


class User(BaseModel):
    id: int = Field(..., example=1)
    email: EmailStr = Field(..., example="gaylord@gmail.com")
    first_name: str = Field(..., example="Гейлорд")
    last_name: str = Field(..., example="Стимбет")
    middle_name: Optional[str] = Field(None, example="Эпифаний")
    is_active: bool = Field(False, example=False)
    is_verified: bool = Field(False, example=False)
    roles: list[Role] = Field(
        ...,
        example=[
            {
                "id": 1,
                "name": "Администратор",
                "slug": "admin",
            },
        ],
    )

    model_config = ConfigDict(from_attributes=True)

    def get_role_names(self) -> list[str]:
        return [role.name for role in self.roles]


class UserCreate(CreateUpdateDictModel):
    email: EmailStr = Field(..., example="ivanov_ivan_ivanovich@mail.ru")
    password: str = Field(..., example="сильныйпароль123")
    first_name: str = Field(..., example="Иван")
    last_name: str = Field(..., example="Иванов")
    middle_name: Optional[str] = Field(None, example="Иванович")
    is_active: Optional[bool] = Field(True, example=False)
    is_verified: Optional[bool] = Field(False, example=False)
    role_ids: list[int] = Field(..., example=[1, 2])


class UserUpdate(CreateUpdateDictModel):
    email: Optional[EmailStr] = Field(None, example="petrov_petr_petrovich@yandex.ru")
    password: Optional[str] = Field(None, example="новыйсильныйпароль123")
    first_name: Optional[str] = Field(None, example="Петр")
    last_name: Optional[str] = Field(None, example="Петров")
    middle_name: Optional[str] = Field(None, example="Петрович")
    is_active: Optional[bool] = Field(None, example=False)
    is_verified: Optional[bool] = Field(None, example=False)
    role_ids: Optional[list[int]] = Field(None, example=[2, 3])
