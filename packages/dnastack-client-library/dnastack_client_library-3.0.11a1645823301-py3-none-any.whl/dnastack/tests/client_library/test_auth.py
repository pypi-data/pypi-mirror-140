from unittest import skipIf

from uuid import uuid4

from dnastack import DataConnectClient
from dnastack.auth.authorizers import ClientCredentialsAuth, DeviceCodeAuth, PersonalAccessTokenAuth
from dnastack.configuration import Authentication, ServiceEndpoint, Oauth2Authentication
from dnastack.helpers.environments import env, flag
from dnastack.tests.exam_helper import token_endpoint, device_code_endpoint, client_secret, client_id, \
    authorization_endpoint, personal_access_endpoint, redirect_url, ExtendedBaseTestCase


class TestAuthentication(ExtendedBaseTestCase):
    """
    Test authentication flows

    .. note:: The URL used in the authorization tests are fake.
    """

    test_resource_url = env('E2E_PROTECTED_DATA_CONNECT_URL', default='https://data-connect-trino.viral.ai/')

    def test_client_credentials_flow(self):
        auth = ClientCredentialsAuth(self.__create_endpoint(
            client_id=client_id,
            client_secret=client_secret,
            grant_type='client_credentials',
            resource_url=self.test_resource_url,
            token_endpoint=token_endpoint
        ))
        auth.authorize('https://dnastack.com')
        auth_session = auth.session
        self.assertIsNotNone(auth_session)
        self.assert_not_empty(auth_session.access_token, 'empty access token')
        self.assertIsNone(auth_session.refresh_token, 'non-empty refresh token')
        self.assertGreater(auth_session.valid_until, 0)

    def test_personal_access_token_flow(self):
        email = env('E2E_AUTH_TEST_PAT_EMAIL')
        token = env('E2E_AUTH_TEST_PAT_TOKEN')

        if not email or not token:
            self.skipTest('The PAT flow test does not have both email and token.')

        auth = PersonalAccessTokenAuth(self.__create_endpoint(
            authorization_endpoint=authorization_endpoint,
            client_id=client_id,
            client_secret=client_secret,
            grant_type='authorization_code',
            personal_access_endpoint=personal_access_endpoint,
            personal_access_email=email,
            personal_access_token=token,
            redirect_url=redirect_url,
            resource_url=self.test_resource_url,
            token_endpoint=token_endpoint,
        ))
        auth.authorize('https://dnastack.com')
        auth_session = auth.session
        self.assertIsNotNone(auth_session)
        self.assert_not_empty(auth_session.access_token, 'empty access token')
        self.assert_not_empty(auth_session.refresh_token, 'empty refresh token')
        self.assertGreater(auth_session.valid_until, 0)

    def __create_endpoint(self, **kwargs) -> ServiceEndpoint:
        return ServiceEndpoint(
            id=f'auto-test-{uuid4()}',
            adapter_type=DataConnectClient.get_adapter_type(),
            url=self.test_resource_url,
            authentication=Authentication(oauth2=Oauth2Authentication(**kwargs)),
        )

# class TestClientLibraryAuthCommand(unittest.TestCase):
#     def setUp(self):
#         self.dataconnect_url = TEST_DATA_CONNECT_URI
#         self.collections_url = TEST_COLLECTIONS_URI
#
#         self.oauth_client = DEFAULT_AUTH_CLIENT
#
#         self.auth = PersonalAccessTokenAuth(email=TEST_WALLET_EMAIL,
#                                             access_token=TEST_WALLET_PERSONAL_ACCESS_TOKEN_PUBLISHER,
#                                             oauth_client=self.oauth_client)
#         self.publisher_client = PublisherClient(
#             dataconnect_url=self.dataconnect_url,
#             collections_url=self.collections_url,
#             auth=self.auth,
#         )
#
#     def test_login_nested_client(self):
#         self.publisher_client.dataconnect.authorize()
#         self.assertIsNotNone(self.publisher_client.auth.get_access_token(url=self.dataconnect_url))
#
#     def test_login_bad_credentials(self):
#         self.publisher_client.personal_access_token = "badtoken"
#         with self.assertRaises(Exception) as ctx:
#             self.publisher_client.dataconnect.authorize()
#             self.assertIsNotNone(ctx.exception.message)
#             self.assertIn(
#                 "The personal access token and/or email provided is invalid",
#                 ctx.exception.message,
#             )
#
#     def test_login_bad_drs_server(self):
#         with self.assertRaises(Exception) as ctx:
#             self.publisher_client.files.authorize(drs_server="badserver")
#             self.assertIsNotNone(ctx.exception.message)
#             self.assertIn("The authorization failed", ctx.exception.message)
#
#     def test_refresh_token(self):
#         # first we must clear the existing token and replace with just a refresh_token
#
#         refresh_auth = RefreshTokenAuth(
#             refresh_token=TEST_WALLET_REFRESH_TOKEN["publisher"],
#             oauth_client=self.publisher_client.auth.oauth_client,
#         )
#         self.publisher_client.dataconnect.auth = refresh_auth
#
#         self.publisher_client.auth.token_store.clear()
#
#         self.publisher_client.dataconnect.authorize()
#
#         self.assertIsNotNone(
#             self.publisher_client.dataconnect.auth.token_store.get_token(
#                 Request(url=self.dataconnect_url)
#             )
#         )
#
#     def test_refresh_token_missing_token(self):
#         with self.assertRaises(Exception) as ctx:
#             self.publisher_client.auth.oauth[
#                 self.publisher_client.dataconnect.get_auth_url()
#             ] = {}
#             self.publisher_client.auth.refresh_token_for_service(
#                 service_type="dataconnect"
#             )
#
#             self.assertIsNotNone(ctx.exception.message)
#             self.assertIn(
#                 "There is no refresh token configured.", ctx.exception.message
#             )
#
#     def test_refresh_token_bad_token(self):
#         with self.assertRaises(Exception) as ctx:
#             self.publisher_client.auth.oauth[
#                 self.publisher_client.dataconnect.get_wallet_url()
#             ] = {}
#             self.publisher_client.auth.set_refresh_token_for_service(
#                 service_type="dataconnect", token="badrefresh"
#             )
#
#             self.publisher_client.auth.refresh_token_for_service(
#                 service_type="dataconnect"
#             )
#
#             self.assertIsNotNone(ctx.exception.message)
#             self.assertIn(
#                 "There is no refresh token configured.", ctx.exception.message
#             )
