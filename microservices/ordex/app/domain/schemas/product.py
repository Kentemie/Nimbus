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


class Product(CreateUpdateDictModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Название продукта")
    price: float = Field(..., example=99.99)

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(CreateUpdateDictModel):
    name: str = Field(..., example="Новое название")
    price: float = Field(..., example=49.99)


class ProductUpdate(CreateUpdateDictModel):
    name: Optional[str] = Field(None, example="Обновлённое название")
    price: Optional[float] = Field(None, example=59.99)
