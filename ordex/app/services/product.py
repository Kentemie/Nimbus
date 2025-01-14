from domain.exceptions import RecordNotFoundException  # noqa
from domain.models import Product as ProductModel
from domain.schemas import ProductCreate, ProductUpdate
from repositories.postgres import ProductRepository


class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    async def get_by_id(self, product_id: int) -> ProductModel:
        product = await self.product_repository.get_by_id(product_id)

        if product is None:
            raise RecordNotFoundException(product_id)

        return product

    async def create(self, product_create: ProductCreate) -> ProductModel:
        return await self.product_repository.create(
            product_create.get_create_update_dict()
        )

    async def update(
        self, product_update: ProductUpdate, product: ProductModel
    ) -> ProductModel:
        return await self.product_repository.update(
            product, product_update.get_create_update_dict()
        )

    async def delete(self, product: ProductModel) -> None:
        await self.product_repository.delete(product)
