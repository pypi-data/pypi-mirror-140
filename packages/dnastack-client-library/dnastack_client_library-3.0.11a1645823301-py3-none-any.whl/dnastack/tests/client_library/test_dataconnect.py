import os.path

from dnastack import DataConnectClient
from dnastack.auth.authorizers import ClientCredentialsAuth
from dnastack.client.base_exceptions import UnauthenticatedApiAccessError, ApiError
from dnastack.configuration import ServiceEndpoint
from dnastack.helpers.environments import env
from dnastack.helpers.logger import get_logger
from dnastack.tests.exam_helper import initialize_test_endpoint, measure_runtime, ReversibleTestCase

_logger = get_logger(os.path.basename(__file__))


class TestDataConnectClient(ReversibleTestCase):
    """ Test a client for Data Connect Service """

    # Test-specified
    endpoint = initialize_test_endpoint(DataConnectClient.get_adapter_type(),
                                        env('E2E_PROTECTED_DATA_CONNECT_URL', default='https://data-connect-trino.viral.ai/'))

    def test_unauthenticated_client_accessing_protected_service_receives_http_401(self):
        client = DataConnectClient.make(ServiceEndpoint(id='abc', adapter_type='data_connect', url=self.endpoint.url))

        with self.assertRaises(UnauthenticatedApiAccessError):
            __ = self._query(client, 'SELECT 1')

    def test_auth_client_performs_random_valid_queries(self):
        client = DataConnectClient.make(self.endpoint)

        # language=sql
        rows = self._query(client, 'SELECT 1')

        self.assertEqual(len(rows), 1)

    def test_auth_client_interacts_with_data_connect_service(self):
        client = DataConnectClient.make(self.endpoint)

        # Drain the whole list to ensure that the iterator can drain the result.
        with measure_runtime('List tables'):
            tables = client.list_tables()

        # Assume that the test environment has at least one tables.
        self.assertGreaterEqual(len(tables), 1)

        first_listed_table = tables[0]

        table_info = client.get_table(first_listed_table.name)

        self.assertEqual(table_info.name, first_listed_table.name)
        self.assertTrue('properties' in table_info.data_model)

        # Run a query from the first table
        with measure_runtime('Query the first 10 items'):
            # language=sql
            rows = self._query(client, f'SELECT * FROM {table_info.name} LIMIT 10')

        self.assertGreaterEqual(len(rows), 1, 'Should have at least one row')

        # Handle invalid columns
        with self.assertRaisesRegex(ApiError, r'(C|c)olumn'):
            # language=sql
            __ = self._query(client, f'SELECT panda FROM {table_info.name} LIMIT 10')

        # Handle unknown catalog/schema/table
        with self.assertRaisesRegex(ApiError, r'(S|s)chema'):
            # language=sql
            __ = self._query(client, f'SELECT * FROM foo LIMIT 10')

    @staticmethod
    def _query(client: DataConnectClient, query: str):
        return [row for row in client.query(query)]

