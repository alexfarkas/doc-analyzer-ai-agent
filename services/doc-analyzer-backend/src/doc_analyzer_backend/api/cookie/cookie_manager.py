import logging
import os
from dataclasses import dataclass

from fastapi import Response

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CookieParams:
    key: str
    path: str
    max_age: int
    domain: str | None = None


def _get_cookie_domain() -> str | None:
    """
    Возвращает domain для cookie.
    None означает, что cookie будет привязан к текущему домену.
    """
    domain = os.getenv("COOKIE_DOMAIN")
    if domain:
        return domain
    return None


SESSION_COOKIE = CookieParams(
    key="session_id",
    path="/",
    max_age=24 * 3600,
    domain=_get_cookie_domain(),
)


def _set_cookie(response: Response, params: CookieParams, value: str):
    logger.debug(f"== SET COOKIE DEBUG ==")
    logger.debug(f"Key: {params.key}")
    logger.debug(f"Value: {value}")
    logger.debug(f"Domain: {params.domain}")
    logger.debug(f"Path: {params.path}")
    logger.debug(f"Secure: False")
    logger.debug(f"HttpOnly: True")
    logger.debug(f"SameSite: lax")
    logger.debug(f"======================")

    response.set_cookie(
        key=params.key,
        value=value,
        domain=params.domain,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=params.max_age,
        path=params.path,
    )


def set_session_cookie(response: Response, value: str):
    _set_cookie(response, SESSION_COOKIE, value)
