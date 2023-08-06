import re

from dnastack.helpers.environments import env
from dnastack.tests.cli.base import CliTestCase
from dnastack.tests.exam_helper import client_id, client_secret, token_endpoint


class TestCollectionsCommand(CliTestCase):
    _base_config = {
        '.mode': 'standard',
        '.authentication.oauth2.client_id': client_id,
        '.authentication.oauth2.client_secret': client_secret,
        '.authentication.oauth2.grant_type': 'client_credentials',
        '.authentication.oauth2.token_endpoint': token_endpoint,
    }

    def setUp(self) -> None:
        super().setUp()

        endpoints = [
            ('collections', 'E2E_COLLECTION_SERVICE_URL', 'https://collection-service.viral.ai/'),
            ('data_connect', 'E2E_PROTECTED_DATA_CONNECT_URL', 'https://data-connect-trino.viral.ai/'),
        ]

        client_mode = env('E2E_CLIENT_MODE', required=False)

        final_config = dict()

        for adapter_type, var_name, default in endpoints:
            endpoint_url = env(var_name, default=default)
            final_config[f'{adapter_type}.url'] = endpoint_url
            final_config[f'{adapter_type}.authentication.oauth2.resource_url'] = endpoint_url
            final_config.update({
                adapter_type + suffix: value
                for suffix, value in self._base_config.items()
            })
            if client_mode:
                final_config[f'{adapter_type}.mode'] = client_mode

        self._configure(final_config)
        # self.execute(f'cat {self._config_file_path}')

    def test_happy_path(self):
        # Test listing collection
        collections = self.simple_invoke('collections', 'list')
        self.assertGreaterEqual(len(collections), 1, 'Must have at least one collection for this test')

        first_collection = collections[0]
        self.assertIn('id', first_collection)
        self.assertIn('name', first_collection)
        self.assertIn('slugName', first_collection)
        self.assertIn('description', first_collection)
        self.assertIn('itemsQuery', first_collection)

        id = first_collection['slugName']

        # Test listing tables in the collection
        tables = self.simple_invoke('collections', 'tables', 'list', first_collection['slugName'])
        self.assertGreaterEqual(len(tables), 0)

        # Prepare for the test query.
        max_size = 10
        query = first_collection['itemsQuery']
        # Limit the result
        if re.search(r' limit \d+\s?', query, re.I):
            query = query + ' LIMIT ' + max_size

        # JSON version
        rows = self.simple_invoke('collections', 'query', id, query)
        self.assertLessEqual(len(rows), max_size, f'Expected upto {max_size} rows')

        # CSV version
        result = self.invoke('collections', 'query', id, query, '-f', 'csv')
        lines = result.output.split('\n')
        self.assertLessEqual(len(lines), max_size + 1, f'Expected upto {max_size} lines, excluding headers')
        for line in lines:
            if not line.strip():
                continue
            self.assertTrue(',' in line, f'The content does not seem to be a CSV-formatted string.')
