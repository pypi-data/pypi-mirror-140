"""OAuth2 providers library."""

__all__ = ["oauth2providers"]

from .discord import discord
from .google import google


oauth2providers = {
    "discord": discord,
    "google": google,
}
