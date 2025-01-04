import base64
import hashlib
import logging
import os
import re
from homeassistant.components.application_credentials import (
    AuthImplementation, AuthorizationServer, ClientCredential)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from typing import Any

from .const import (BUDGETTHUIS_AUTH_URL, BUDGETTHUIS_CLIENT_ID, BUDGETTHUIS_REDIRECT_URI,
                    BUDGETTHUIS_SCOPE, BUDGETTHUIS_TOKEN_URL)

_LOGGER = logging.getLogger(__name__)


class OAuth2Impl(AuthImplementation):
    """Custom OAuth2 implementation."""

    code_challenge: str | None
    code_verifier: str | None

    def __init__(self, hass: HomeAssistant, auth_domain: str, credential: ClientCredential,
                 authorization_server: AuthorizationServer, code_challenge: str | None,
                 code_verifier: str | None) -> None:
        super().__init__(hass, auth_domain, credential, authorization_server)

        self.code_verifier = code_verifier
        self.code_challenge = code_challenge

    @property
    def redirect_uri(self) -> str:
        return BUDGETTHUIS_REDIRECT_URI

    @property
    def extra_authorize_data(self) -> dict:
        return {
            "scope": BUDGETTHUIS_SCOPE,
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256"
        }

    async def async_resolve_external_data(self, external_data: Any) -> dict:
        """Resolve the authorization code to tokens."""
        return await self._token_request(
            {
                "grant_type": "authorization_code",
                "code": external_data["code"],
                "redirect_uri": external_data["state"]["redirect_uri"],
                "code_verifier": self.code_verifier
            }
        )


async def async_get_auth_implementation(
        hass: HomeAssistant, auth_domain: str, credential: ClientCredential
) -> config_entry_oauth2_flow.AbstractOAuth2Implementation:
    """Return auth implementation for a custom auth implementation."""

    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)

    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')

    return OAuth2Impl(
        hass,
        auth_domain,
        ClientCredential(
            client_id=BUDGETTHUIS_CLIENT_ID,
            client_secret=""
        ),
        AuthorizationServer(
            authorize_url=BUDGETTHUIS_AUTH_URL,
            token_url=BUDGETTHUIS_TOKEN_URL
        ),
        code_challenge=code_challenge,
        code_verifier=code_verifier
    )
