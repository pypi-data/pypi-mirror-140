from pprint import pformat
from pydantic import BaseModel, ValidationError
from requests import Session, JSONDecodeError
from typing import Optional, Any, Dict, List, Iterator
from urllib.parse import urljoin

from dnastack.client.base_client import BaseServiceClient
from dnastack.client.base_exceptions import UnauthenticatedApiAccessError, UnauthorizedApiAccessError, ApiError, \
    MissingResourceError, ServerApiError
from dnastack.client.result_iterator import ResultLoader, ResultIterator
from dnastack.configuration import ServiceEndpoint


class InactiveQuerySessionError(StopIteration):
    """ Raised when the query loader has ended its session """


class TableNotFoundError(MissingResourceError):
    """ Raised when the requested table is not found """


class Error(BaseModel):
    status: Any
    title: str
    details: Optional[str]


class Table(BaseModel):
    name: str
    description: Optional[str]
    data_model: Optional[Dict[str, Any]]
    errors: Optional[List[Error]]


class Pagination(BaseModel):
    next_page_url: Optional[str]


class TableDataResponse(BaseModel):
    data: Optional[List[Dict[str, Any]]]
    data_model: Optional[Dict[str, Any]] = list()
    pagination: Optional[Pagination]
    errors: Optional[List[Error]]


class ListTablesResponse(BaseModel):
    tables: Optional[List[Table]]
    pagination: Optional[Pagination]
    errors: Optional[List[Error]]


class TableListLoader(ResultLoader):
    def __init__(self, session: Session, initial_url: str):
        self.__session = session
        self.__initial_url = initial_url
        self.__current_url: Optional[str] = None
        self.__active = True

    def load(self) -> List[Table]:
        if not self.__active:
            raise InactiveQuerySessionError(self.__initial_url)

        session = self.__session
        response = session.get(self.__current_url or self.__initial_url)
        status_code = response.status_code

        if status_code == 401:
            raise UnauthenticatedApiAccessError(self.__generate_api_error_feedback())
        elif status_code == 403:
            raise UnauthorizedApiAccessError(self.__generate_api_error_feedback())
        elif status_code >= 400:  # Catch all errors
            raise ApiError(self.__initial_url, status_code, response.text)

        try:
            response_body = response.json() if response.text else dict()
        except JSONDecodeError as error:
            raise ApiError(self.__initial_url, status_code,
                           f"Could not deserialize JSON. Actual response:\n{response.text}") from error

        try:

            if isinstance(response_body, list):
                api_response = ListTablesResponse(tables=response_body)
            else:
                api_response = ListTablesResponse(**response_body)
        except ValidationError:
            raise ServerApiError(f'Invalid Response Body: {response_body}')

        self.logger.debug(f'Response:\n{pformat(response_body, indent=2)}')

        if api_response.errors:
            extracted_errors = [
                f'{e["title"]} ({e["source"]})'
                for e in api_response.errors
            ]

            self.__active = False

            if self.__current_url:
                # The iterator encounters an unexpected error while iterating the result. Return an empty list.
                self.logger.warning(
                    f'While listing tables from {self.__initial_url}, the server failed to respond to the request to '
                    f'{self.__current_url} due to errors and the client will return the data received so far.'
                )
            else:
                # The iterator encounters an error on the first request.
                self.logger.error(f'The server responds an error while making a request to {self.__initial_url}.')

            self.logger.warning(f'The errors are: {extracted_errors}')
            return []

        ########################################################################################################################################################
        # FIXME The failed build is due that listing table from publisher_data fails. The code should throw an exception if all requests during listing fails. #
        ########################################################################################################################################################

        self.__current_url = api_response.pagination.next_page_url if api_response.pagination else None
        if not self.__current_url:
            self.__active = False

        return api_response.tables

    def has_more(self) -> bool:
        return self.__active or self.__current_url

    def close(self):
        self.__active = False

    def __generate_api_error_feedback(self, response_body) -> str:
        if self.__current_url:
            return f'Failed to load a follow-up page of the table list from {self.__current_url}:\n\n{response_body}'
        else:
            return f'Failed to load the first page of the table list from {self.__initial_url}:\n\n{response_body}'


class QueryLoader(ResultLoader):
    def __init__(self, session: Session, initial_url: str, query: Optional[str] = None):
        self.__session = session
        self.__initial_url = initial_url
        self.__current_url: Optional[str] = None
        self.__query = query
        self.__active = True

    def load(self) -> List[Dict[str, Any]]:
        if not self.__active:
            raise InactiveQuerySessionError(self.__initial_url)

        session = self.__session

        if not self.__current_url:
            # Load the initial page.
            if self.__query:
                # Send a search request
                response = session.post(self.__initial_url, json=dict(query=self.__query))
            else:
                # Fetch the table data
                response = session.get(self.__initial_url)
        else:
            # Load a follow-up page.
            response = session.get(self.__current_url)

        status_code = response.status_code
        response_body = response.json() if response.text else dict()
        self.logger.debug(f'Response (JSON):\n{pformat(response_body, indent=2)}')

        if status_code == 401:
            raise UnauthenticatedApiAccessError(self.__generate_api_error_feedback(response_body))
        elif status_code == 403:
            raise UnauthorizedApiAccessError(self.__generate_api_error_feedback(response_body))
        elif status_code == 404:
            raise MissingResourceError(self.__generate_api_error_feedback(response_body))
        elif status_code >= 400:  # Catch all errors
            try:
                error_response = TableDataResponse(**response_body)
                error_feedback = ', '.join([e.title for e in error_response.errors])
            except:
                error_feedback = response_body
            raise ApiError(self.__initial_url, status_code, error_feedback)

        api_response = TableDataResponse(**response_body)

        if api_response.errors:
            extracted_errors = [
                f'{e["title"]} ({e["source"]})'
                for e in api_response.errors
            ]

            self.__active = False

            if self.__current_url:
                # The iterator encounters an unexpected error while iterating the result. Return an empty list.
                self.logger.warning(
                    f'While listing tables from {self.__initial_url}, the server failed to respond to the request to '
                    f'{self.__current_url} due to errors and the client will return the data received so far.'
                )
            else:
                # The iterator encounters an error on the first request.
                self.logger.error(f'The server responds an error while making a request to {self.__initial_url}.')

            self.logger.warning(f'The errors are: {extracted_errors}')
            return []

        self.__current_url = api_response.pagination.next_page_url if api_response.pagination else None
        if not self.__current_url:
            self.__active = False

        return api_response.data

    def has_more(self) -> bool:
        return self.__active or self.__current_url

    def close(self):
        self.__active = False

    def __generate_api_error_feedback(self, response_body=None) -> str:
        if self.__query:
            if self.__current_url:
                return f'Failed to load a follow-up page of the result from this query:\n\n{self.__query}\n\nResponse:\n{response_body}'
            else:
                return f'Failed to load the first page of the result from this query:\n\n{self.__query}\n\nResponse:\n{response_body}'
        else:
            if self.__current_url:
                return f'Failed to load a follow-up page of {self.__current_url}'
            else:
                return f'Failed to load the first page of {self.__initial_url}'


class DataConnectClient(BaseServiceClient):
    """
    A Client for the GA4GH Data Connect standard
    """

    def __init__(self, endpoint: ServiceEndpoint):
        if not endpoint.url.endswith('/'):
            endpoint.url = endpoint.url + r'/'

        super().__init__(endpoint)

    @staticmethod
    def get_adapter_type() -> str:
        return 'data_connect'

    def query(self, query: str) -> Iterator[Dict[str, Any]]:
        """ Run an SQL query """

        return ResultIterator(QueryLoader(self.client, urljoin(self.url, r'search'), query))

    def iterate_tables(self) -> Iterator[Table]:
        """ Iterate the list of tables """
        return ResultIterator(TableListLoader(self.client, urljoin(self.url, r'tables')))

    def list_tables(self) -> List[Table]:
        """ List all tables """
        return [t for t in self.iterate_tables()]

    def get_table(self, table_name: str) -> Table:
        """ Get table metadata """
        response = self.client.get(urljoin(self.url, f'table/{table_name}/info'))
        status_code = response.status_code
        response_body = response.json()

        if status_code == 401:
            raise UnauthenticatedApiAccessError('Authentication required')
        elif status_code == 403:
            raise UnauthorizedApiAccessError('Insufficient privilege')
        elif status_code == 404:
            raise TableNotFoundError(table_name)
        elif status_code >= 400:  # Catch all errors
            raise ApiError(self.url, status_code, response_body)

        return Table(**response_body)
