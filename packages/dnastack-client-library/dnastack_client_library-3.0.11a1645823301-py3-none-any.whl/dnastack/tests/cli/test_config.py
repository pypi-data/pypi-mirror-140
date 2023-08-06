import traceback

from dnastack.tests.cli.base import CliTestCase


class TestConfiguration(CliTestCase):
    def test_list_available_properties(self):
        result = self.invoke('config', 'available-properties')
        self.assertIn('collections.url', result.output)
        self.assertIn('data_connect.authentication.oauth2.client_id', result.output)

    def test_crud_operations(self):
        # Get all configurations when there is nothing defined.
        result = self.invoke('config', 'list')
        self.assertEqual('{}',
                         result.output.strip(),
                         'When the configuration file does not exist, it should show as empty string.')

        # Get the property when there is nothing defined.
        result = self.invoke('config', 'get', 'data_connect.url')
        self.assertEqual('null',
                         result.output.strip(),
                         'When the configuration is not set, it should show as empty string.')

        # Set the property.
        self.invoke('config', 'set', 'data_connect.url', 'https://data-connect.dnastack.com', bypass_error=False)
        self.assert_config_property('data_connect.url', 'https://data-connect.dnastack.com', 'Set the endpoint URL')

        # Set the nested property.
        self.invoke('config', 'set', 'data_connect.authentication.oauth2.client_id', 'foo', bypass_error=False)
        self.assert_config_property('data_connect.url', 'https://data-connect.dnastack.com',
                                    'The endpoint URL should remain the same after dealing with one nested property.')
        self.assert_config_property('data_connect.authentication.oauth2.client_id', 'foo',
                                    'The client ID should be set to the expected value.')

        self.invoke('config', 'set', 'data_connect.authentication.oauth2.client_secret', 'bar', bypass_error=False)
        self.assert_config_property('data_connect.url', 'https://data-connect.dnastack.com',
                                    'The endpoint URL should remain the same after dealing with two nested properties.')
        self.assert_config_property('data_connect.authentication.oauth2.client_id', 'foo',
                                    'The client ID should remain the same after dealing with two nested properties.')
        self.assert_config_property('data_connect.authentication.oauth2.client_secret', 'bar',
                                    'The client secret should be set to the expected value.')

    def assert_config_property(self, property_path: str, expected_value: str, summary: str):
        result = self.invoke('config', 'get', property_path)
        given_value = result.output.strip()
        self.assertEqual(expected_value, given_value,
                         f'Summary: {summary}\nExpected: [{expected_value}]\nGiven: [{given_value}]')
