from pydantic import BaseModel, Field, SecretStr


class AuthLoginRequest(BaseModel):
    email: str = Field(min_length=1)
    password: SecretStr = Field(min_length=8)


class ChangePasswordRequest(AuthLoginRequest):
    new_password: SecretStr = Field(min_length=8, max_length=8)


class AuthTokenResponse(BaseModel):
    jwt: str
    token_type: str = "bearer"
