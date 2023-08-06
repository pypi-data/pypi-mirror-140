"""Yet another OAuth2 library (for FastAPI).


TODO:

 - Token refresh
 - Configurable scopes
 - Provider for Slack

"""

__all__ = ["YAOAuth2", "OAuth2Data"]


from .router import YAOAuth2
from .models import OAuth2Data
