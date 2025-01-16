from fastapi import status

from .errors import ErrorModel, ErrorCode

from domain.types import OpenAPIResponseType

unauthorized_response: OpenAPIResponseType = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.MISSING_TOKEN: {
                        "summary": "Отсутствует токен или пользователь неактивен.",
                        "value": {"detail": ErrorCode.MISSING_TOKEN},
                    },
                }
            }
        },
    },
}

forbidden_response: OpenAPIResponseType = {
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.FORBIDDEN_OPERATION: {
                        "summary": "Вам не разрешено выполнять эту операцию.",
                        "value": {"detail": ErrorCode.FORBIDDEN_OPERATION},
                    },
                }
            }
        },
    }
}
