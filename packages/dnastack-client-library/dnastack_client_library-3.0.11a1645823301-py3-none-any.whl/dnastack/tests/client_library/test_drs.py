import os

from urllib.parse import urlparse

from time import time

from dnastack.auth.authorizers import ClientCredentialsAuth
from dnastack.exceptions import DRSDownloadException
from dnastack.helpers.environments import env
from dnastack.tests.exam_helper import initialize_test_endpoint, ReversibleTestCase, ExtendedBaseTestCase
from dnastack.client.collections_client import CollectionServiceClient, Collection
from dnastack.client.dataconnect_client import DataConnectClient
from dnastack.client.files_client import DrsClient, _module_pandas_available


class TestDrsClient(ReversibleTestCase, ExtendedBaseTestCase):
    """ Test a client for DRS service"""

    # Test-specified

    # Set up the client for the collection service
    collection_endpoint = initialize_test_endpoint(CollectionServiceClient.get_adapter_type(),
                                                   env('E2E_COLLECTION_SERVICE_URL',
                                                       default='https://collection-service.viral.ai/'))
    collection_client = CollectionServiceClient.make(collection_endpoint)

    # Set up the client for the data connect service
    data_connect_endpoint = initialize_test_endpoint(DataConnectClient.get_adapter_type(),
                                                     env('E2E_PROTECTED_DATA_CONNECT_URL',
                                                         default='https://data-connect-trino.viral.ai/'))
    data_connect_client = DataConnectClient.make(data_connect_endpoint)

    # Set up the client for the data repository service
    # NOTE: We use the collection service for this test as the service implements DRS interfaces.
    drs_endpoint = initialize_test_endpoint(DrsClient.get_adapter_type(),
                                            env('E2E_PROTECTED_DRS_URL',
                                                default='https://collection-service.viral.ai/'))
    drs_client = DrsClient.make(drs_endpoint)

    # Find the library table.
    # NOTE: Assume that the table exists.
    library_table = [t for t in data_connect_client.iterate_tables() if t.name.endswith('.public.library')][0]

    def setUp(self):
        super(TestDrsClient, self).setUp()
        self.output_dir = os.path.join(os.path.dirname(__file__), 'tmp')
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self) -> None:
        super(TestDrsClient, self).tearDown()
        for file_name in os.listdir(self.output_dir):
            if file_name[0] == '.':
                continue
            os.unlink(os.path.join(self.output_dir, file_name))

    def test_download_files(self):
        if not _module_pandas_available:
            self.skipTest('The library pandas is not available for this test.')

        # Set up a test collection with blobs
        # language=sql
        collection_query = f"SELECT * FROM {self.library_table.name} WHERE type='blob' LIMIT 20"

        items = [i for i in self.data_connect_client.query(collection_query)]

        if not items:
            self.fail('Precondition failed: No blobs available')

        collection = self.collection_client.create(Collection.make(f'zero-test-{time()}', collection_query))
        self.after_this_test(self.collection_client.delete, collection)

        # Define the test DRS URL
        drs_net_location = urlparse(self.drs_endpoint.url).netloc
        drs_urls = []
        expected_file_names = set()
        for item in items:
            item_id = item['id']
            expected_file_names.add(os.path.basename(item['name']))
            drs_urls.append(f'drs://{drs_net_location}/{item_id}')

        # Attempt to download the data.
        self.drs_client.download_files(urls=drs_urls, output_dir=self.output_dir)

        existing_file_names = os.listdir(self.output_dir)
        self.assertGreater(len(existing_file_names), 0)

        download_contents = []
        self.drs_client.download_files(urls=drs_urls, out=download_contents)
        self.assertGreater(len(drs_urls), len(download_contents))
        for download_content in download_contents:
            self.assert_not_empty(download_content)

    def test_downloading_files_with_invalid_urls_raises_error(self):
        drs_net_location = urlparse(self.drs_endpoint.url).netloc
        with self.assertRaises(DRSDownloadException):
            self.drs_client.download_files(urls=[f'drs://{drs_net_location}/foo-bar'])

        with self.assertRaises(DRSDownloadException):
            self.drs_client.download_files(urls=[f'drs://shiroyuki.com/foo-bar'])

        with self.assertRaises(DRSDownloadException):
            self.drs_client.download_files(urls=[f'drs://qwerty.asdf/foo-bar'])
