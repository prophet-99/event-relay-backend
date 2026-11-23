from datetime import datetime, timedelta, timezone

from jwt import encode

from app.settings.app_settings import get_app_settings


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
