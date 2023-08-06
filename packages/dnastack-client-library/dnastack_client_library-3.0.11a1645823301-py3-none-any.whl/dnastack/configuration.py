import os
import shutil
import yaml
from imagination.decorator import service, EnvironmentVariable
from pydantic import BaseModel
from typing import List, Optional, Dict
from uuid import uuid4

from dnastack.constants import CLI_DIRECTORY
from dnastack.helpers.logger import get_logger


class Oauth2Authentication(BaseModel):
    """OAuth2 Authentication Information"""
    authorization_endpoint: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]
    device_code_endpoint: Optional[str]
    grant_type: str
    personal_access_endpoint: Optional[str]
    personal_access_email: Optional[str]
    personal_access_token: Optional[str]
    redirect_url: Optional[str]
    resource_url: str
    scope: Optional[str]
    token_endpoint: Optional[str]
    type: str = 'oauth2'


class AwsAuthentication(BaseModel):
    """Authentication Information with AWS"""
    access_key_id: str
    access_key_secret: str
    host: str
    region: str
    service: str = "execute-api"
    token: Optional[str]
    type: str = 'aws-sigv4'


class Authentication(BaseModel):
    """Authentication Information"""
    aws: Optional[AwsAuthentication]
    oauth2: Optional[Oauth2Authentication]


class ServiceEndpoint(BaseModel):
    """API Service Endpoint"""
    id: str = str(uuid4())
    """Local ID"""

    adapter_type: str
    """Adapter type"""

    authentication: Optional[Authentication]

    url: str
    """Base URL"""

    mode: str = 'explorer'
    """ Client mode ("standard" or "explorer") - only applicable if the client supports. """


class ConfigurationError(RuntimeError):
    """ General Error. """


class MissingEndpointError(ConfigurationError):
    """ Raised when a request endpoint is not registered. """


class Configuration(BaseModel):
    """Configuration (v3)"""
    __logger = get_logger('Configuration')

    version: int = 3
    defaults: Dict[str, str] = dict()  # adapter-type-to-service-id
    endpoints: List[ServiceEndpoint] = list()

    def set_default(self, adapter_type: str, endpoint_id: str):
        self.__logger.debug(f'adapter_type = {adapter_type}, endpoint_id = {id}')

        try:
            self.get_endpoint_or_default(adapter_type, endpoint_id, create_default_if_missing=False)
        except MissingEndpointError:
            raise ConfigurationError(f"Could not set default, not {adapter_type} adapter with id {endpoint_id}")

        self.defaults[adapter_type] = endpoint_id

    def remove_endpoint(self, adapter_type: str, endpoint_id: str):
        self.__logger.debug(f'endpoint_id = {endpoint_id}')
        self.endpoints = [endpoint for endpoint in self.endpoints if
                          endpoint.id != endpoint_id and endpoint.adapter_type != adapter_type]

        if adapter_type in self.defaults and self.defaults[adapter_type] == endpoint_id:
            del self.defaults[adapter_type]

    def add_endpoint(self, endpoint_id: str, adapter_type: str, url: str = None):
        self.__logger.debug(f'adapter_type = {adapter_type}, url = {url}')

        if self.endpoint_exists(endpoint_id=endpoint_id, adapter_type=adapter_type):
            raise ConfigurationError(f"Could not add endpoint, found existing one with id {endpoint_id}")
        endpoint_url: str = url or ''
        endpoint = ServiceEndpoint(id=endpoint_id, adapter_type=adapter_type, url=endpoint_url)
        self.endpoints.append(endpoint)

        if adapter_type in self.defaults and not self.defaults[adapter_type]:
            self.defaults[adapter_type] = endpoint_id

        return endpoint

    def endpoint_exists(self, endpoint_id: str, adapter_type: str):
        try:
            return self.get_endpoint(adapter_type, endpoint_id=endpoint_id, create_default_if_missing=False) is not None
        except MissingEndpointError:
            return False

    def get_all_endpoints_by(self,
                             adapter_type: Optional[str] = None,
                             endpoint_id: Optional[str] = None) -> List[ServiceEndpoint]:
        return [
            endpoint for endpoint in self.endpoints
            if (
                    (adapter_type is not None and endpoint.adapter_type == adapter_type)
                    or (endpoint_id is not None and endpoint.id == endpoint_id)
            )
        ]

    def get_endpoint_or_default(self, adapter_type: str,
                                endpoint_id: Optional[str] = None,
                                create_default_if_missing=False) -> ServiceEndpoint:
        try:
            return self.get_endpoint(adapter_type, endpoint_id=endpoint_id,
                                     create_default_if_missing=create_default_if_missing)
        except MissingEndpointError as e:
            if adapter_type in self.defaults:
                return self.get_endpoint(adapter_type, endpoint_id=self.defaults[adapter_type])
            else:
                raise e

    def get_endpoint(self,
                     adapter_type: str,
                     endpoint_id: Optional[str] = None,
                     create_default_if_missing=False) -> ServiceEndpoint:
        endpoints: List[ServiceEndpoint] = self.get_all_endpoints_by(adapter_type, endpoint_id)
        endpoint: Optional[ServiceEndpoint] = None

        try:
            endpoint = endpoints[0]
        except IndexError:
            pass

        # When the endpoint is not available...
        if endpoint is None:
            if create_default_if_missing:
                endpoint = ServiceEndpoint(id=str(uuid4()), adapter_type=adapter_type, url='')  # Leave to an empty URL
                self.endpoints.append(endpoint)
                self.defaults[adapter_type] = endpoint.id
            else:
                raise MissingEndpointError(f'The "{adapter_type}" endpoint #{endpoint_id or "?"} is not defined.')

        return endpoint


@service.registered(
    params=[
        EnvironmentVariable('DNASTACK_CONFIG_FILE', default=os.path.join(CLI_DIRECTORY, 'config.yaml'),
                            allow_default=True)
    ]
)
class ConfigurationManager:
    def __init__(self, file_path: str):
        self.__logger = get_logger(f'{type(self).__name__}')
        self.__file_path = file_path
        self.__swap_file_path = f'{self.__file_path}.swp'

    def load_raw(self):
        if not os.path.exists(self.__file_path):
            return '{}'
        with open(self.__file_path, 'r') as f:
            return f.read()

    def load(self):
        config = Configuration(**yaml.load(self.load_raw(), Loader=yaml.SafeLoader))
        return config

    def save(self, configuration: Configuration):
        # Note (1): This is designed to have file operation done as quickly as possible to reduce race conditions.
        # Note (2): Instead of interfering with the main file directly, the new content is written to a temp file before
        #           swapping with the real file to minimize the I/O block.
        new_content = yaml.dump(configuration.dict(), Dumper=yaml.SafeDumper)
        with open(self.__swap_file_path, 'w') as f:
            f.write(new_content)
        shutil.copyfile(self.__swap_file_path, self.__file_path)
        os.unlink(self.__swap_file_path)
