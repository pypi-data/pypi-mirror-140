"""Settings for Google OAuth2."""

__all__ = ["google"]

from ..models import OAuth2Provider, OAuth2UserInfo


GOOGLE_API_URL = 'https://www.googleapis.com/'
METADATA_URL = 'https://accounts.google.com/.well-known/openid-configuration'


def parse_user(user: dict) -> OAuth2UserInfo:
    print(user)
    return OAuth2UserInfo(
        sub=user.get("sub"),
        username=user.get("name"),
        full_name=user.get("name"),
        email=user.get("email"),
        avatar_url=user.get("picture"),
        locale=user.get("locale"),
    )


google = OAuth2Provider(
    api_base_url=GOOGLE_API_URL,
    authorization_endpoint='https://accounts.google.com/o/oauth2/v2/auth',
    token_endpoint='https://oauth2.googleapis.com/token',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    revocation_endpoint='https://oauth2.googleapis.com/revoke',
    userinfo_parser=parse_user,
    scope="openid email profile",
)
