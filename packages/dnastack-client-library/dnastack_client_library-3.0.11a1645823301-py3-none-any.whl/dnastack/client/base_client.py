import requests
from requests import Session
from requests.auth import AuthBase
from typing import TypeVar
from uuid import uuid4

from dnastack.helpers.logger import get_logger
from ..auth import OAuthTokenAuth
from ..auth.auth_factory import AuthFactory
from ..configuration import ServiceEndpoint


class BaseServiceClient:
    """ The base class for all DNAStack Clients """

    def __init__(self, endpoint: ServiceEndpoint):
        self._uuid = str(uuid4())
        self._endpoint = endpoint
        self._client = requests.Session()
        self._authorized = False
        self._logger = get_logger(type(self).__name__)
        self._auth = (
            AuthFactory.create_from(endpoint=endpoint, cache_key=endpoint.id)
            if endpoint.authentication
            else None
        )

        self._logger.debug(f'auth => {self._auth}')

        if self._auth:
            self._client.auth = self._auth

    def __del__(self):
        self.close()

    def close(self):
        if self._client:
            self._client.close()

    @staticmethod
    def get_adapter_type() -> str:
        """Get the descriptive adapter type"""
        ...

    @property
    def url(self):
        """The base URL to the endpoint"""
        return self._endpoint.url

    @property
    def auth(self) -> AuthBase:
        """Request Authenticator

        *This is for internal uses only.*
        """
        return self._auth

    @auth.setter
    def auth(self, auth: AuthBase) -> None:
        self._auth = auth
        self._client.auth = auth
        self._authorized = False

    @property
    def client(self) -> Session:
        """HTTP Client

        *This is for internal uses only.*
        """
        return self._client

    def authorize(self):
        """.. deprecated:: v3.1"""
        if self._authorized:
            return

        if isinstance(self._auth, OAuthTokenAuth):
            self._auth.authorize(self.url)
            self._authorized = True
        else:
            t: TypeVar = type(self._auth)
            self._logger.info(
                f'The {t.__module__}.{t.__name__} auth base will probably authenticate/authorize this client on demand.'
            )

    @classmethod
    def make(cls, endpoint: ServiceEndpoint):
        """Create this class with the given `endpoint`."""
        return cls(endpoint)
