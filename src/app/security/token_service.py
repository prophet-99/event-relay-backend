import logging
from datetime import datetime, timedelta, timezone

from jwt import (
    ExpiredSignatureError,
    InvalidTokenError,
    MissingRequiredClaimError,
    decode,
    encode,
)
from pydantic import ValidationError

from app.security.exceptions import (
    ExpiredAccessTokenException,
    InvalidTokenException,
    RequiredClaimsTokenException,
)
from app.security.schemas import AccessTokenPayload
from app.settings.app_settings import get_app_settings

logger: logging.Logger = logging.getLogger(name=__name__)


def create_access_token(user_id: int) -> str:
    app_settings = get_app_settings()

    expire_at = datetime.now(tz=timezone.utc) + timedelta(
        minutes=app_settings.jwt_access_token_expire_minutes
    )
    payload = {"sub": str(user_id), "exp": expire_at}

    return encode(
        payload=payload,
        algorithm=app_settings.jwt_algorithm,
        key=app_settings.jwt_secret_key,
    )


def extract_payload(jwt: str) -> AccessTokenPayload:
    try:
        app_settings = get_app_settings()
        jwt_payload = decode(
            jwt=jwt,
            algorithms=[app_settings.jwt_algorithm],
            key=app_settings.jwt_secret_key,
            options={"require": ["sub", "exp"]},
        )

        return AccessTokenPayload.model_validate(jwt_payload)
    except ExpiredSignatureError as exc:
        logger.warning(msg="The JWT expires")
        raise ExpiredAccessTokenException() from exc

    except MissingRequiredClaimError as exc:
        logger.warning(msg="The JWT claims has been modified")
        raise RequiredClaimsTokenException() from exc

    except ValidationError as exc:
        logger.warning(msg="Invalid exp value or sub is not a number")
        raise InvalidTokenException() from exc

    except InvalidTokenError as exc:
        logger.error(msg="A JWT error decode ocurred")
        raise InvalidTokenException() from exc
