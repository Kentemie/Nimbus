from typing import (
    Union,
    Any,
    TypeVar,
    Coroutine,
    AsyncGenerator,
    Generator,
    AsyncIterator,
    Callable,
)

OpenAPIResponseType = dict[Union[int, str], dict[str, Any]]

RETURN_TYPE = TypeVar("RETURN_TYPE")

DependencyCallable = Callable[
    ...,
    Union[
        RETURN_TYPE,
        Coroutine[None, None, RETURN_TYPE],
        AsyncGenerator[RETURN_TYPE, None],
        Generator[RETURN_TYPE, None, None],
        AsyncIterator[RETURN_TYPE],
    ],
]
