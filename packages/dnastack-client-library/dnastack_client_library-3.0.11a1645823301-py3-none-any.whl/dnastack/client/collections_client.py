import re
from pydantic import BaseModel
from requests import Response
from requests.auth import AuthBase
from time import time
from typing import List, Iterator, Optional, Union, Any, Dict
from urllib.parse import urljoin

from .base_client import BaseServiceClient
from .dataconnect_client import DataConnectClient, Table
from ..configuration import ServiceEndpoint
from ..exceptions import ServiceException


def _raise_error(url: str, res: Response, primary_reason: str):
    summary = f'Unexpected Error: HTTP {res.status_code}'
    detail = primary_reason

    if res.status_code == 401:
        summary = "Authentication Required"
    elif res.status_code == 403:
        summary = "Access Denied"
    elif res.status_code == 404:
        summary = "Not Found"
    else:
        response_json = res.json()
        if 'message' in response_json:
            # Handle a generic error response from the service.
            detail += f' ({response_json["message"]})'
        elif "errors" in response_json and response_json['errors'] and 'title' in response_json['errors'][0]:
            detail += f' ({", ".join([e["title"] for e in response_json["errors"]])})'
        else:
            detail += f' ({response_json})'

    raise ServiceException(msg=f'{summary}: {detail}', url=url)


class UnsupportedClientModeError(RuntimeError):
    """ Raised when the specified mode is incompatible or supported """


class Collection(BaseModel):
    """
    A model representing a collection

    .. note:: This is not a full representation of the object.
    """

    id: Optional[str]
    name: str
    slugName: str
    description: Optional[str]
    itemsQuery: str

    @classmethod
    def make(cls,
             name: str,
             items_query: str,
             slug_name: Optional[str] = None,
             description: Optional[str] = None):
        if not slug_name:
            slug_name = re.sub(r'[^a-z0-9-]', '-', name.lower()) + str(int(time()))
            slug_name = re.sub(r'-+', '-', slug_name)
        return cls(name=name, itemsQuery=items_query, slugName=slug_name, description=description)


class CollectionServiceClient(BaseServiceClient):
    """Client for Collection API"""

    def __init__(self, endpoint: ServiceEndpoint):
        if not endpoint.url.endswith(r'/'):
            endpoint.url = endpoint.url + r'/'

        super(CollectionServiceClient, self).__init__(endpoint)

    @staticmethod
    def get_adapter_type() -> str:
        return 'collections'

    def create(self, collection: Collection) -> Collection:
        """ Create a new collection """
        create_response = self.client.post(urljoin(self.url, 'collections'), json=collection.dict())
        if not create_response.ok:
            _raise_error(self.url, create_response, 'Unable to create the collection')
        return Collection(**create_response.json())

    def _get_single_collection_url(self, id_or_slug_name: str, extended_path: str = ''):
        if self._endpoint.mode == 'standard':
            return urljoin(self.url, f'collection/{id_or_slug_name}{extended_path}')
        if self._endpoint.mode == 'explorer':
            return urljoin(self.url, f'collections/{id_or_slug_name}{extended_path}')
        else:
            raise UnsupportedClientModeError(self._endpoint.mode)

    def get(self, id_or_slug_name: str) -> Collection:
        """ Get a collection by ID or slug name """
        get_response = self.client.get(self._get_single_collection_url(id_or_slug_name))
        if not get_response.ok:
            _raise_error(self.url, get_response, 'Collection not found')

        return Collection(**get_response.json())

    def delete(self, collection: Collection, ignore_error: bool = False):
        """ Delete the collection """
        assert collection.id, 'Invalid collection ID'
        self.delete_by_id(collection.id, ignore_error)

    def delete_by_id(self, id_or_slug_name: str, ignore_error: bool = False):
        """ Delete the collection by ID """
        delete_response = self.client.delete(self._get_single_collection_url(id_or_slug_name))
        if delete_response.status_code != 204 and not ignore_error:
            _raise_error(self.url, delete_response, 'Unable to delete the collection')

    def update(self, collection: Collection) -> Collection:
        """ Perform a delta update on the collection """
        collection_url = self._get_single_collection_url(collection.id)

        get_response = self.client.get(collection_url)
        if not get_response.ok:
            _raise_error(self.url, get_response, 'The collection no longer exists')

        existing_collection = Collection(**get_response.json())
        version = get_response.headers['etag'].replace(r'"', '')

        json_patch = []
        for property_name in dir(collection):
            if property_name[0] == '_':
                continue

            new_value = getattr(collection, property_name)
            if callable(new_value):
                continue

            old_value = getattr(existing_collection, property_name)
            if new_value == old_value:
                continue

            json_patch.append(dict(op='replace', path=f'/{property_name}', value=new_value))

        patch_response = self.client.patch(collection_url, json=json_patch, headers={'If-Match': version})
        if not patch_response.ok:
            _raise_error(self.url, patch_response, 'Failed to update the collection')

        return Collection(**patch_response.json())

    def list_collections(self) -> List[Collection]:
        """ List all available collections """
        res = self.client.get(urljoin(self.url, 'collections'))

        if not res.ok:
            _raise_error(self.url, res, "Unable to list collections")

        return [Collection(**raw_collection) for raw_collection in res.json()]

    def get_data_connect_client(self, collection: Union[str, Collection]) -> DataConnectClient:
        """ Get the Data Connect client for the given collection (ID, slug name, or collection object) """
        collection_id = None
        if isinstance(collection, Collection):
            collection_id = collection.id
        elif isinstance(collection, str):
            collection_id = collection
        else:
            raise TypeError(f'Unexpected type: {type(collection).__name__}')

        sub_endpoint = ServiceEndpoint(**self._endpoint.dict())
        sub_endpoint.url = self._get_single_collection_url(collection_id, '/data-connect/')

        return DataConnectClient.make(sub_endpoint)

    def list_tables(self, collection_id_or_slug_name: str) -> List[Table]:
        """
        Returns a list of table within the specified collection

        .. deprecated:: 3.0
            Will be removed in 3.1
        """
        # TODO Remove this method in 3.1
        return self.get_data_connect_client(collection_id_or_slug_name).list_tables()

    def query(self, collection_id_or_slug_name: str, query: str) -> Iterator[Dict[str, Any]]:
        """
        Execute a SQL query against a collection

        .. deprecated:: 3.0
            Will be removed in 3.1
        """
        # TODO Remove this method in 3.1
        return self.get_data_connect_client(collection_id_or_slug_name).query(query)


# Temporarily for backward compatibility
CollectionsClient = CollectionServiceClient
