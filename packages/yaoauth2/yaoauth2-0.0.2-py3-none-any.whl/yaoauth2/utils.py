"""OAuth2 token management."""

import httpx

from .config import oauth2config, OAuth2ProviderConfig


def get_provider_config(name: str) -> OAuth2ProviderConfig | None:
    """Return site-specific OAuth2 provider configuration.

    Basically it means client_id and client_secret for the provider.
    Return None if the provider is not enabled.
    """
    for provider in oauth2config.providers:
        if provider.provider == name:
            return provider
    return None


async def get_user_info(provider, access_token: str):
    """Get normalized user info from the OAuth2 provider."""

    # TODO: Some exception handling here

    async with httpx.AsyncClient() as client:
        res = await client.get(
            provider.userinfo_endpoint,
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )
    if res.status_code != 200:
        return None

    user_data = res.json()
    return provider.userinfo_parser(user_data)
