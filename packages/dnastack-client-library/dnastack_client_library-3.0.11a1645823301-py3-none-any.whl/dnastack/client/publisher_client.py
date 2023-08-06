import os
from imagination import container
from typing import Union, List, Any, Optional

from .base_client import BaseServiceClient
from .collections_client import CollectionServiceClient
from .dataconnect_client import DataConnectClient
from .files_client import DrsClient
from .wes_client import WesClient
from ..configuration import ConfigurationManager, MissingEndpointError
from ..helpers.logger import get_logger


class PublisherClient:
    """
    A Client for DNAStack suite of products (Data Connect, WES, Collections, etc.)

    All sub-clients are automatically initiated with the configuration of the default service endpoint of each sub-client type (as known as "adapter type"), defined in the configuration file.
    """

    def __init__(self):
        config_manager: ConfigurationManager = container.get(ConfigurationManager)
        config = config_manager.load()

        self._logger = get_logger(type(self).__name__)

        for cls in [CollectionServiceClient, DataConnectClient, DrsClient, WesClient]:
            adapter_type = cls.get_adapter_type()
            property_name = f'_{adapter_type}'

            try:
                default_endpoint = config.get_endpoint_or_default(adapter_type, create_default_if_missing=False)
                setattr(self, property_name, cls.make(default_endpoint))
            except MissingEndpointError:
                self._logger.warning(f'There exists no default {adapter_type} endpoint configured and the client is '
                                     f'not available for this type of service.')
                setattr(self, property_name, None)

    @property
    def dataconnect(self) -> Optional[DataConnectClient]:
        """
        ..deprecated: v3.1
        """
        return self._data_connect

    @dataconnect.setter
    def dataconnect(self, client: DataConnectClient):
        """
        ..deprecated: v3.1
        """
        assert client is None or isinstance(client, DataConnectClient)
        self._data_connect = client

    @property
    def data_connect(self) -> Optional[DataConnectClient]:
        """ The client for the default data connect endpoint """
        return self._data_connect

    @data_connect.setter
    def data_connect(self, client: DataConnectClient):
        assert client is None or isinstance(client, DataConnectClient)
        self._data_connect = client

    @property
    def collections(self) -> Optional[CollectionServiceClient]:
        """ The client for the default collection API endpoint """
        return self._collections

    @collections.setter
    def collections(self, client: CollectionServiceClient):
        assert client is None or isinstance(client, CollectionServiceClient)
        self._collections = client

    @property
    def wes(self) -> Optional[WesClient]:
        """ The client for the default WES endpoint """
        return self._wes

    @wes.setter
    def wes(self, client: WesClient):
        assert client is None or isinstance(client, WesClient)
        self._wes = client

    @property
    def files(self) -> DrsClient:
        """ The client for the default data repository service (DRS) endpoint """
        return self._drs

    @files.setter
    def files(self, client: DrsClient):
        assert client is None or isinstance(client, DrsClient)
        self._drs = client

    def get_services(self) -> List[BaseServiceClient]:
        """
        Return all configured services.

        :return: List of all configured clients (dataconnect, collections, wes)
        """
        return [self.dataconnect, self.collections, self.wes]

    def load(self, urls: Union[str, List[str]]) -> Any:
        """
        Return the raw output of one or more DRS resources

        :param urls: One or a list of DRS urls (drs://...)
        :return: The raw output of the specified DRS resource
        """
        if isinstance(urls, str):
            urls = [urls]

        download_content = []

        self.files.download_files(
            urls=urls,
            display_progress_bar=False,
            out=download_content,
        )
        return download_content

    def download(
        self,
        urls: Union[str, List[str]],
        output_dir: str = os.getcwd(),
        display_progress_bar: bool = False,
    ) -> None:
        """
        Download one or more DRS resources from the specified urls

        :param urls: One or a list of DRS urls (drs://...)
        :param output_dir: The directory to output the downloaded files to.
        :param display_progress_bar: Display the progress of the downloads. This is False by default
        :return:
        """
        if isinstance(urls, str):
            urls = [urls]

        self.files.download_files(
            urls=urls,
            output_dir=output_dir,
            display_progress_bar=display_progress_bar,
        )
