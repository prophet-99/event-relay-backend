from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class JwtSettings:
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int


@pytest.fixture(name="jwt_settings")
def create_jwt_settings(monkeypatch: pytest.MonkeyPatch) -> JwtSettings:
    settings = JwtSettings(
        jwt_secret_key="test-secret-key-with-at-least-32-bytes",
        jwt_algorithm="HS256",
        jwt_access_token_expire_minutes=60,
    )
    monkeypatch.setattr("app.security.token_service.get_app_settings", lambda: settings)
    return settings
