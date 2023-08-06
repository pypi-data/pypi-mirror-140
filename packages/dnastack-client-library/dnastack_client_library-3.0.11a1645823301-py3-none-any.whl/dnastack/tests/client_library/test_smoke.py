from dnastack import CollectionServiceClient
from dnastack.configuration import ServiceEndpoint
from dnastack.helpers.logger import get_logger
from dnastack.tests.exam_helper import ExtendedBaseTestCase


class TestSmoke(ExtendedBaseTestCase):
    _logger = get_logger('lib/smoke_test')

    def test_demo(self):
        """
        This is based on the public documentation.

        .. note:: This test is specifically designed for a certain deployment.
        """
        client = CollectionServiceClient.make(ServiceEndpoint(adapter_type='collections',
                                                              url='https://viral.ai/api/',
                                                              mode='explorer'))
        self._logger.debug('Listing collections...')
        collections = client.list_collections()
        assert len(collections) > 0, 'Should have at least ONE collection'

        collection_name = 'ncbi-sra'

        self._logger.debug('Listing tables...')
        tables = client.list_tables(collection_name)
        assert len(tables) > 0, 'Should have at least ONE table'

        self._logger.debug('Querying...')
        query = 'SELECT * FROM publisher_data.ncbi_sra.variants LIMIT 200000'
        row_count = 0
        for row in client.query(collection_name, query):
            row_count += 1
            if row_count % 10000 == 0:
                self._logger.debug(f'Receiving {row_count} rows...')
            self.assertGreater(len(row.keys()), 0)
        self._logger.debug(f'Received {row_count} row(s)')

        assert row_count > 0, 'Should have at least ONE row'
        assert row_count > 50000, 'Should have at least 100k rows'