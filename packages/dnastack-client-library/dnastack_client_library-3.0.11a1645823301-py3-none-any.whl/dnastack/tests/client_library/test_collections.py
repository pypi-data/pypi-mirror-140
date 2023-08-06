from time import time

from dnastack.client.collections_client import CollectionServiceClient, Collection
from dnastack.client.dataconnect_client import DataConnectClient
from dnastack.configuration import ServiceEndpoint
from dnastack.exceptions import ServiceException
from dnastack.helpers.environments import env
from dnastack.helpers.logger import get_logger
from dnastack.tests.exam_helper import initialize_test_endpoint, ReversibleTestCase, ExtendedBaseTestCase


class TestCollectionsClient(ReversibleTestCase, ExtendedBaseTestCase):
    """ Test a client for Collection Service """

    # Test-specified
    collection_endpoint = initialize_test_endpoint(CollectionServiceClient.get_adapter_type(),
                                                   env('E2E_COLLECTION_SERVICE_URL',
                                                       default='https://collection-service.viral.ai/'))
    data_connect_endpoint = initialize_test_endpoint(DataConnectClient.get_adapter_type(),
                                                     env('E2E_PROTECTED_DATA_CONNECT_URL',
                                                         default='https://data-connect-trino.viral.ai/'))

    def test_auth_client_interacts_with_collection_api(self):
        collection_client = CollectionServiceClient.make(self.collection_endpoint)

        collections = collection_client.list_collections()

        self.assertGreater(len(collections), 0)
        self.assertIsInstance(collections[0], Collection)

        # Perform CRUD operations on collections
        collection_name = f'zero-test-{int(time())}'
        collection = collection_client.create(Collection.make(name=collection_name, items_query='SELECT 1'))
        self.after_this_test(collection_client.delete, collection, ignore_error=True)

        collection_id = collection.id

        self.assert_not_empty(collection.id)
        self.assert_not_empty(collection.slugName)

        collection_client.delete(collection)

        with self.assertRaisesRegex(ServiceException, 'Collection not found'):
            collection_client.get(collection_id)

    def test_auth_client_interacts_with_data_connect_api(self):
        collection_client = CollectionServiceClient.make(self.collection_endpoint)
        data_connect_client = DataConnectClient.make(self.data_connect_endpoint)

        # Get the information to create the items query.
        tables = data_connect_client.list_tables()
        if not tables:
            self.fail('Precondition failed: No table available')
        table_name = tables[0].name
        # language=sql
        items_query = f"SELECT * FROM library WHERE preferred_name = '{table_name}'"
        test_query = f'SELECT * FROM {table_name} LIMIT 2'

        # Create a test collection.
        collection_name = f'zero-test-{int(time())}'
        collection = collection_client.create(Collection.make(name=collection_name, items_query=items_query))
        self.after_this_test(collection_client.delete, collection, ignore_error=True)

        # New APIs
        collect_data_connect_client = collection_client.get_data_connect_client(collection)
        self.assert_not_empty(collect_data_connect_client.list_tables())
        self.assert_not_empty([row for row in collect_data_connect_client.query(test_query)])

        # Legacy APIs
        self.assert_not_empty(collection_client.list_tables(collection.id))
        self.assert_not_empty([row for row in collection_client.query(collection.id, test_query)])
