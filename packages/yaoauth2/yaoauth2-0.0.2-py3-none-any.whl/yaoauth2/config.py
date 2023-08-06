"""OAuth module configuration."""

__all__ = ["oauth2config"]

from pydantic import BaseModel, Field
from typing import Callable


callback_description = """Callback to be called when a user logs in.

This callback is called with the user's Oauth data, and should return a
coroutine that resolves to a dict-like object containing the response.
e.g. session id, local user data etc.
"""


class OAuth2ProviderConfig(BaseModel):
    provider: str
    client_id: str
    client_secret: str


class OAuth2Config(BaseModel):
    """OAuth module configuration."""

    providers: list[OAuth2ProviderConfig] = Field(
        default_factory=list,
        description="List of OAuth providers to enable."
    )

    login_callback: Callable | None = Field(
        None,
        description=callback_description
    )
    login_response_model: BaseModel | None = None

    enable_redirect_endpoint: bool = True

    def add_provider(self, name: str, client_id: str, client_secret: str):
        self.providers.append(
            OAuth2ProviderConfig(
                provider=name,
                client_id=client_id,
                client_secret=client_secret
            )
        )


oauth2config = OAuth2Config()
