from typing import Any, Dict, List

from dnastack.client.dataconnect_client import TableNotFoundError
from dnastack.helpers.environments import env
from dnastack.tests.cli.base import CliTestCase
from dnastack.tests.exam_helper import client_id, client_secret, token_endpoint


class TestDataConnectCommand(CliTestCase):
    test_resource_url = env('E2E_PROTECTED_DATA_CONNECT_URL', default='https://data-connect-trino.viral.ai/')

    def setUp(self) -> None:
        super().setUp()
        self._configure({
            'data_connect.authentication.oauth2.client_id': client_id,
            'data_connect.authentication.oauth2.client_secret': client_secret,
            'data_connect.authentication.oauth2.grant_type': 'client_credentials',
            'data_connect.authentication.oauth2.resource_url': self.test_resource_url,
            'data_connect.authentication.oauth2.token_endpoint': token_endpoint,
            'data_connect.url': self.test_resource_url,
        })

    def test_query_and_get_json(self):
        result = self.invoke('dataconnect', 'query', 'SELECT 1 AS x, 2 AS y')
        self.assertEqual(0, result.exit_code)
        rows = self.parse_json(result.output)
        self.assertEqual(1, len(rows))
        self.assertEqual(1, rows[0]['x'])
        self.assertEqual(2, rows[0]['y'])

    def test_query_and_get_csv(self):
        result = self.invoke('dataconnect', 'query', 'SELECT 1 AS x, 2 AS y', '-f', 'csv')
        self.assertEqual(0, result.exit_code)
        self.assertEqual('x,y\n1,2', result.output.strip())

    def test_full_functionalities(self):
        tables = self.simple_invoke('dataconnect', 'tables', 'list')
        self.__run_test_table_and_search_apis(tables)

    def __run_test_table_and_search_apis(self, tables: List[Dict[str, Any]], test_table_index = 0):
        first_listed_table_info = tables[test_table_index]

        table_info = self.simple_invoke('dataconnect', 'tables', 'get', first_listed_table_info['name'])
        self.assertEqual(first_listed_table_info['name'], table_info['name'])
        table_columns = table_info['data_model']['properties']

        max_size = 123
        max_columns = 5
        sample_table_name = table_info['name']
        sample_column_names = list(table_columns.keys())[:max_columns]
        sample_column_names_string = ', '.join(sample_column_names)

        rows = self.simple_invoke('dataconnect', 'query',
                                  f'SELECT {sample_column_names_string} FROM {sample_table_name} LIMIT {max_size}')

        if len(rows) == 0:
            self._logger.warning(f'T/{sample_table_name} has not enough data for testing.')
            if test_table_index >= len(tables):
                self.fail('No tables with enough data for testing')
            else:
                self._logger.info('Trying the next table...')
                self.__run_test_table_and_search_apis(tables, test_table_index + 1)

        self.assertGreaterEqual(max_size, len(rows), f'Expected upto {max_size} row(s)')

        selected_column_names = list(rows[0].keys())

        self.assertGreaterEqual(max_columns, len(selected_column_names), f'Expected upto {max_columns} column(s)')
        self.assertEqual(sorted(sample_column_names), sorted(selected_column_names),
                         f'Expected columns: {sample_column_names}')

    def test_get_unknown_table(self):
        with self.assertRaises(TableNotFoundError):
            self.invoke('dataconnect', 'tables', 'get', 'foo_bar')
