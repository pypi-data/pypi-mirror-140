import time
import httpx

from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from .providers import oauth2providers
from .models import OAuth2Option, OAuth2Options, OAuth2Data
from .config import oauth2config
from .utils import get_provider_config, get_user_info


#
# OAuth2 options
#
# Returns a list of available OAuth2 providers.
# Along with the provider name, the URL to the
# authorization endpoint, scope and the client_id.
#
# This is used by the frontend to display a list
# of available OAuth2 providers.
#


async def oauth2_options(request: Request):
    """Return a list of available OAuth2 providers."""
    result = []
    for name, provider in oauth2providers.items():
        provider_config = get_provider_config(name)
        if not provider_config:
            continue
        result.append(OAuth2Option(
            name=name,
            url=provider.authorization_endpoint,
            client_id=provider_config.client_id,
            scope=provider.scope,
        ))
    return OAuth2Options(options=result)


#
# OAuth2 redirect
#
# This endpoint redirects the user to the OAuth2 provider's login page.
# The user is redirected back to the application after the login process is
# complete.
#
# This is used only for testing - in production, the fron-end application
# should handle the redirection process.
#


async def oauth2_redirect(request: Request, provider_name: str):
    """Redirect to the OAuth provider's login page."""
    try:
        provider = oauth2providers[provider_name]
    except KeyError:
        return {"error": "Provider not found"}
    if not (provider_config := get_provider_config(provider_name)):
        return {"error": f"{provider_name} authorization is not enabled"}

    redirect_url = request.url_for(
        'oauth2_callback',
        provider_name=provider_name
    )

    uri = provider.authorization_endpoint
    uri += "?client_id=" + provider_config.client_id
    uri += "&redirect_uri=" + redirect_url
    uri += "&response_type=code"
    return RedirectResponse(uri)


#
# OAuth2 Callback
#
# This is the callback endpoint for OAuth2 providers.
# It is called by the OAuth2 provider after the user has
# authenticated and been redirected back to the application.
#
# The callback endpoint validates the OAuth2 code and exchanges
# it for an access token.
#

async def oauth2_login(
    request: Request,
    provider_name: str,
    redirect_uri: str = None,
    code: str = None,
):
    try:
        provider = oauth2providers[provider_name]
    except KeyError:
        return {"error": "Provider not found"}

    if not (provider_config := get_provider_config(provider_name)):
        return {"error": f"{provider_name} authorization is not enabled"}

    if not code:
        return {"error": "No code provided"}

    if not redirect_uri:
        return {"error": "No redirect URI provided"}

    # Call the OAuth2 provider's token endpoint
    # and exchange the code for an access token.

    redirect_uri = redirect_uri or request.url_for(
        'oauth2_login',
        provider_name=provider_name
    )

    async with httpx.AsyncClient() as client:
        res = await client.post(provider.token_endpoint, data={
            "grant_type": "authorization_code",
            "client_id": provider_config.client_id,
            "client_secret": provider_config.client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        })

    if res.status_code != 200:
        return {"error": "Failed to get token"}

    token_data = res.json()
    token = {"access_token": token_data["access_token"]}

    if "refresh_token" in token_data:
        token["refresh_token"] = token_data["refresh_token"]

    if "expires_in" in token_data:
        token["expires_at"] = token_data["expires_in"] + int(time.time())
    elif "expires_at" in token_data:
        token_data["expires_at"] = token_data["expires_at"]

    if not (user := await get_user_info(provider, token["access_token"])):
        return {"error": "Failed to get user info"}

    odata = OAuth2Data(
        user=user,
        provider=provider_name,
        **token
    )

    # print(odata.json(indent=4))

    # Either call the callback function or
    # return the user data to the application.

    if oauth2config.login_callback is not None:
        return await oauth2config.login_callback(odata)
    return odata
