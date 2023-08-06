"""Settings for Discord OAuth2."""

__all__ = ["discord"]

from ..models import OAuth2Provider, OAuth2UserInfo


BASE_AVATAR_URL = "https://cdn.discordapp.com/avatars"


def parse_user(user: dict) -> OAuth2UserInfo:
    """Normalize Discord user data."""
    avatar_url = f"{BASE_AVATAR_URL}/{user['id']}/{user['avatar']}.png"

    return OAuth2UserInfo(
        sub=user.get("id", ""),
        username=user.get("username"),
        full_name=user.get("username"),
        email=user.get("email"),
        avatar_url=avatar_url,
        locale=user.get("locale"),
    )


discord = OAuth2Provider(
    api_base_url='https://discordapp.com/api/',
    token_endpoint='https://discordapp.com/api/oauth2/token',
    authorization_endpoint='https://discordapp.com/api/oauth2/authorize',
    userinfo_endpoint='https://discordapp.com/api/users/%40me',
    revocation_endpoint='https://discordapp.com/api/oauth2/token/revoke',
    userinfo_parser=parse_user,
    scope="identify email",
)
