from typing import Optional
from typing import Any
from authlib.jose import JsonWebKey, JsonWebToken
from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    RefreshToken,
)
from fastmcp.server.auth.auth import (
    ClientRegistrationOptions,
    OAuthProvider,
    RevocationOptions,
)
from mcp.shared.auth import (
    OAuthClientInformationFull,
    OAuthToken,
)

    
class CustomAuthProvider(OAuthProvider):
    # --- Unused OAuth server methods ---
    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        raise NotImplementedError("Client management not supported")

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        raise NotImplementedError("Client registration not supported")

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        raise NotImplementedError("Authorization flow not supported")

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthorizationCode | None:
        raise NotImplementedError("Authorization code flow not supported")

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        raise NotImplementedError("Authorization code exchange not supported")

    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> RefreshToken | None:
        raise NotImplementedError("Refresh token flow not supported")

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        raise NotImplementedError("Refresh token exchange not supported")

    async def revoke_token(
        self,
        token: AccessToken | RefreshToken,
    ) -> None:
        raise NotImplementedError("Token revocation not supported")


class AuthTokenAuthProvider(CustomAuthProvider):
    """
    Custom authentication provider that verifies Auth token from Authorization header
    """
    
    def __init__(self, valid_auth_tokens: list[str]):
        """
        Initialize the API Key authentication provider.
        
        Args:
            valid_auth_tokens: List of valid Auth tokens
        """
        self.valid_auth_tokens = valid_auth_tokens
        
        super().__init__(
            issuer_url="https://fastmcp.example.com",
            client_registration_options=ClientRegistrationOptions(enabled=False),
            revocation_options=RevocationOptions(enabled=False),
            required_scopes=None,
        )
    
    async def load_access_token(self, token: str) -> AccessToken | None:
        """
        Validates the provided auth token.

        Args:
            token: The auth token string to validate

        Returns:
            AccessToken object if valid, None if invalid or expired
        """
        try:
            if not token in self.valid_auth_tokens:
                return None
            
            return AccessToken(
                token=token,
                client_id=f"auth_token_{hash(token) % 10000}",
                scopes=["read", "write"],
                expires_at=int(3000000000),
            )
        
        except Exception as e:
            return None