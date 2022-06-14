import logging
from typing import Any, Callable

from aioredis.exceptions import RedisError
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, StarletteHTTPException, ValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api.base import InternalServerError, ProbeError


logger = logging.getLogger(__name__)


class ResourceNotFoundError(Exception):
    """HTTP 404"""


class ErrorResponse(BaseModel):
    """
    Стандартный формат ответа в случае возникновения ошибки.
    """

    error: bool
    message: str
    details: Any


def error_response(status_code: int, message: str, details: Any = None) -> JSONResponse:
    content = ErrorResponse(error=True, message=message, details=details)
    return JSONResponse(status_code=status_code, content=jsonable_encoder(content))


def default_error_handler_creator(resp_status: int) -> Callable:  # pylint: disable=unused-argument
    """
    Ловит и форматирует все дефолтные ошибки.
    """

    async def default_error_handler(
        request: Request, exc: Exception  # pylint: disable=unused-argument
    ) -> JSONResponse:
        if isinstance(exc, (RequestValidationError, ValidationError)):
            return error_response(resp_status, message="Server unable to process user input", details=exc.errors())

        if isinstance(exc, StarletteHTTPException):
            return error_response(exc.status_code, message=exc.detail)

        return error_response(resp_status, message=str(exc))

    return default_error_handler


def setup_exceptions(application: FastAPI) -> None:
    """
    Ловит все исключения, указанные в exc_pairs чтобы формат ответа был стандартным.
    Любые новые неотловленные исключения стоит добавлять сюда.
    """
    exc_pairs = [
        (InternalServerError, default_error_handler_creator(status.HTTP_500_INTERNAL_SERVER_ERROR)),
        (ProbeError, default_error_handler_creator(status.HTTP_503_SERVICE_UNAVAILABLE)),
        (RequestValidationError, default_error_handler_creator(status.HTTP_422_UNPROCESSABLE_ENTITY)),
        (ValidationError, default_error_handler_creator(status.HTTP_422_UNPROCESSABLE_ENTITY)),
        (StarletteHTTPException, default_error_handler_creator(status.HTTP_422_UNPROCESSABLE_ENTITY)),
        (RedisError, default_error_handler_creator(status.HTTP_502_BAD_GATEWAY)),
        (ResourceNotFoundError, default_error_handler_creator(status.HTTP_404_NOT_FOUND)),
    ]

    for err, handler in exc_pairs:
        application.add_exception_handler(err, handler)
