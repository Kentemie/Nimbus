__all__ = [
    "get_auth_router",
    "get_register_router",
    "get_verify_router",
    "get_reset_password_router",
    "get_users_router",
    "get_roles_router",
    "get_orders_router",
    "get_products_router",
]


from .auth import get_auth_router
from .register import get_register_router
from .reset import get_reset_password_router
from .verify import get_verify_router
from .users import get_users_router
from .roles import get_roles_router
from .orders import get_orders_router
from .products import get_products_router
