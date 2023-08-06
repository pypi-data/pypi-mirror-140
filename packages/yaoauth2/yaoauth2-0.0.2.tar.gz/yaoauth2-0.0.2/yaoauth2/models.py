"""Pydantic models for Oauth."""

from typing import Callable
from pydantic import BaseModel, Field


class OAuth2UserInfo(BaseModel):
    """Normalized user information."""

    sub: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")

    avatar_url: str | None = Field(None, description="Avatar URL")
    full_name: str | None = Field(None, description="Full name")
    locale: str | None = Field(None, description="Locale")


class OAuth2Provider(BaseModel):
    """Oauth provider settings."""

    api_base_url: str = Field(..., description="API base URL")
    token_endpoint: str = Field(..., description="Access token URL")
    authorization_endpoint: str = Field(..., description="Authorize URL")
    revocation_endpoint: str = Field(..., description="Revoke URL")
    userinfo_endpoint: str = Field(..., description="User info endpoint")
    userinfo_parser: Callable = Field(..., description="User info parser")
    scope: str = Field(..., description="Scope")


class OAuth2Option(BaseModel):
    """Client facing Oauth provider settings.

    This is used to create a link to the Oauth provider's
    authorization page.
    """

    name: str = Field(..., description="OAuth2 provider name.")
    url: str = Field(..., description="OAuth2 provider authorization URL.")
    client_id: str = Field(..., description="OAuth2 client ID.")
    scope: str = Field(..., description="Scope")


class OAuth2Options(BaseModel):
    """List of client facing Oauth provider settings."""

    options: list[OAuth2Option]


class OAuth2Data(BaseModel):
    """Oauth data to be stored in a session.

    If a login callback is defined, it is called with the OauthData object
    as the first argument.

    Otherwise, the data is returned to the client.
    """

    user: OAuth2UserInfo = Field(..., description="User information.")
    provider: str = Field(..., description="Name of the OAuth2 provider")
    access_token: str = Field(..., description="OAuth2 access token")

    refresh_token: str | None = Field(
        None,
        description="OAuth2 refresh token"
    )

    expires_at: int | None = Field(
        None,
        description="OAuth2 token expiration time"
    )
