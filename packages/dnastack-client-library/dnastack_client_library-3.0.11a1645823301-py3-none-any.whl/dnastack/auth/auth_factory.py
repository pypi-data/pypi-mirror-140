from imagination.decorator import service
from requests.auth import AuthBase
from typing import Dict, Optional

from dnastack.auth import DeviceCodeAuth, PersonalAccessTokenAuth
from dnastack.auth.authorizers import ClientCredentialsAuth
from dnastack.auth.authorizers import AwsSigv4Auth

from dnastack.configuration import ServiceEndpoint


class UnsupportedAuthenticationConfigurationError(RuntimeError):
    """ Raised when the authentication configuration is not supported by the factory """


class UnsupportedOAuth2AuthenticationConfigurationError(UnsupportedAuthenticationConfigurationError):
    """ Raised when the OAuth2 authentication configuration is not supported by the factory """


@service.registered()
class AuthFactory:
    _known_authorizers: Dict[str, AuthBase] = dict()

    @staticmethod
    def create_from(endpoint: ServiceEndpoint, cache_key: Optional[str] = None):
        if cache_key in AuthFactory._known_authorizers:
            return AuthFactory._known_authorizers[cache_key]

        auth_info = endpoint.authentication

        if not auth_info:
            return None

        if auth_info.oauth2:
            oauth2_auth_info = auth_info.oauth2
            if oauth2_auth_info.grant_type == 'authorization_code' and oauth2_auth_info.personal_access_token \
                    and oauth2_auth_info.personal_access_email:
                # Personal Access Token
                return PersonalAccessTokenAuth(endpoint=endpoint)
            elif oauth2_auth_info.grant_type == 'client_credentials':
                # Client-Credentials Flow
                return ClientCredentialsAuth(endpoint=endpoint)
            elif oauth2_auth_info.grant_type == 'urn:ietf:params:oauth:grant-type:device_code':
                # Device Code Flow
                return DeviceCodeAuth(endpoint=endpoint)
            else:
                raise UnsupportedOAuth2AuthenticationConfigurationError(oauth2_auth_info)
        elif auth_info.aws:
            return AwsSigv4Auth(endpoint=endpoint)
        else:
            raise NotImplementedError(f'The authentication')