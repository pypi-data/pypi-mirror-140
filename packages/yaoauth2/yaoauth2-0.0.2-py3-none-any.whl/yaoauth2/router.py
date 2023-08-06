"""OAuth2 authentication logic."""

__all__ = ["YAOAuth2"]

import httpx

from fastapi import APIRouter

from .models import OAuth2Data, OAuth2Options
from .config import oauth2config
from .providers import oauth2providers
from .utils import get_provider_config, get_user_info
from .endpoints import oauth2_options, oauth2_redirect, oauth2_login


class YAOAuth2:
    def __init__(self):
        self.config = oauth2config

    #
    # Configuration
    #

    def add_provider(self, name: str, client_id: str, client_secret: str):
        self.config.add_provider(name, client_id, client_secret)

    #
    # FastAPI router
    #

    def create_router(self, **kwargs):
        """Create a FastAPI router for OAuth2 authentication."""

        router = APIRouter(
            **kwargs
        )

        router.add_api_route(
            "/options",
            oauth2_options,
            methods=["GET"],
            description=oauth2_options.__doc__,
            response_model=OAuth2Options
        )

        router.add_api_route(
            "/login/{provider_name}",
            oauth2_login,
            methods=["GET"],
            description=oauth2_login.__doc__,
            response_model=self.config.login_response_model or OAuth2Data
        )

        if self.config.enable_redirect_endpoint:
            router.add_api_route(
                "/redirect/{provider_name}",
                oauth2_redirect,
                methods=["GET"],
                status_code=302,
                description=oauth2_redirect.__doc__
            )

        return router

    #
    # Misc. helpers
    #

    async def get_user_info(self, provider_name: str, access_token: str):
        try:
            provider = oauth2providers[provider_name]
        except KeyError:
            return
        return await get_user_info(provider, access_token)

    async def refresh_token(self, provider_name: str, refresh_token: str):
        """Refresh an access token."""
        try:
            provider = oauth2providers[provider_name]
        except KeyError:
            return
        provider_config = get_provider_config(provider_name)
        if not provider_config:
            return
        # TODO: Implement refresh token

    async def revoke_token(self, provider_name: str, access_token: str):
        """Revoke an access token."""
        try:
            provider = oauth2providers[provider_name]
        except KeyError:
            return
        provider_config = get_provider_config(provider_name)
        if not provider_config:
            return

        async with httpx.AsyncClient() as client:
            res = await client.post(
                provider.revocation_endpoint,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                data={
                    "token": access_token,
                    "token_type_hint": "access_token",
                    "client_id": provider_config.client_id,
                    "client_secret": provider_config.client_secret,
                },
            )

        if res.status_code != 200:
            print(res.text)
            return False
        return True
