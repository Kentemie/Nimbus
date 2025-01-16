from domain.exceptions import RecordNotFoundException  # noqa
from domain.models import Product as ProductModel
from domain.schemas import ProductCreate, ProductUpdate
from repositories.postgres import ProductRepository


class ProductService:
    """
    Сервис для работы с продуктами.

    :param product_repository: Репозиторий продуктов.

    Методы:
    - `get_by_id`: Получение продукта по ID.
    - `create`: Создание нового продукта.
    - `update`: Обновление существующего продукта.
    - `delete`: Удаление продукта.
    """

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    async def get_by_id(self, product_id: int) -> ProductModel:
        """
        Получает продукт по ID.

        :param product_id: Идентификатор продукта.
        :return: Модель продукта.
        :raises RecordNotFoundException: Если продукт не найден.
        """
        product = await self.product_repository.get_by_id(product_id)

        if product is None:
            raise RecordNotFoundException(product_id)

        return product

    async def create(self, product_create: ProductCreate) -> ProductModel:
        """
        Создаёт новый продукт.

        :param product_create: Данные для создания продукта.
        :return: Созданная модель продукта.
        """
        return await self.product_repository.create(
            product_create.get_create_update_dict()
        )

    async def update(
        self, product_update: ProductUpdate, product: ProductModel
    ) -> ProductModel:
        """
        Обновляет существующий продукт.

        :param product_update: Данные для обновления продукта.
        :param product: Модель продукта для обновления.
        :return: Обновлённая модель продукта.
        """
        return await self.product_repository.update(
            product, product_update.get_create_update_dict()
        )

    async def delete(self, product: ProductModel) -> None:
        """
        Удаляет продукт.

        :param product: Модель продукта для удаления.
        """
        await self.product_repository.delete(product)
