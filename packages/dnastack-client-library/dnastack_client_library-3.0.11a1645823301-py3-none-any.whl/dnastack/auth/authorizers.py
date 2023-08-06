from abc import ABC
from json import JSONDecodeError

import hmac
import hashlib
import datetime

import requests
import webbrowser
from bs4 import BeautifulSoup
from imagination import container
from pprint import pformat
from requests import Request
from requests.auth import AuthBase
from time import time, sleep
from typing import AnyStr, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urljoin, quote

from .session_store import SessionStore, Session
from .utils import login_refresh_token
from ..configuration import Authentication, ServiceEndpoint, AwsAuthentication, Oauth2Authentication
from ..exceptions import AuthException, LoginException, InsufficientAuthInfoError, RefreshException
from ..feature_flags import in_global_debug_mode
from dnastack.helpers.logger import get_logger


class OAuthTokenAuth(AuthBase, ABC):
    """
    An AuthBase implementation that caches generated tokens.
    """

    def __init__(self, endpoint: ServiceEndpoint):
        super().__init__()
        self._endpoint = endpoint
        self._logger = get_logger(f'{endpoint.adapter_type}/{endpoint.id}')
        self._session_store: SessionStore = container.get(SessionStore)
        self._session: Optional[Session] = None

    @property
    def _auth_info(self) -> Oauth2Authentication:
        return self._endpoint.authentication.oauth2

    @property
    def session_id(self):
        # This is a simple implementation. It could be done better.
        return self._endpoint.id

    def __call__(self, req: Request) -> Request:
        """
        This function is called by the requests library to modify client requests as they are sent.
        In our case we get an access token then pass it along to

        :param req: The outbound :class:`requests.Request`
        :return: A modified request with the Authorization header set to a Bearer token
        """
        self._logger.debug('Activated')
        session = self.session or self.authorize(req.url)

        req.headers["Authorization"] = f"Bearer {session.access_token}"

        return req

    @property
    def session(self) -> Optional[Session]:
        session = self._session or self._session_store.restore(self.session_id)

        if not session:
            return None
        elif session.is_valid():
            self._session = session
            return session
        else:
            return self.refresh_session()

    def revoke_session(self):
        self._session = None
        self._session_store.delete(self.session_id)

    def authorize(self, request_url: str, **kwargs) -> Session:
        """
        Authorize a request by generating then storing an OAuth access token

        :param request_url: The URL of the request
        :param kwargs: Any additional keyword arguments to be passed to the :method:`generate_access_token` function
        :return: A session object
        """
        if not request_url:
            raise AuthException("There is no url to authorize")

        if self.session:
            return self.session

        self.assert_auth_readiness()

        self._session = self.create_session(request_url, **kwargs)
        self._session_store.save(self.session_id, self._session)

        return self._session

    def create_session(self, request_url: str, **kwargs) -> Session:
        """
        Create a new Session information, including access token, refresh token, etc.
        """
        ...

    def assert_auth_readiness(self):
        """ Assert if the endpoint has enough information to initiate a given OAuth flow """
        ...

    def refresh_session(self) -> Session:
        session = self._session or self._session_store.restore(self.session_id)
        auth_info = self._auth_info
        refresh_token = session.refresh_token

        if not refresh_token:
            raise RefreshException("The refresh token is missing")

        refresh_token_res = requests.post(
            auth_info.token_endpoint,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "scope": auth_info.scope,
            },
            auth=(auth_info.client_id, auth_info.client_secret),
        )

        if refresh_token_res.ok:
            refresh_token_json = refresh_token_res.json()

            if in_global_debug_mode:
                self._logger.debug(f'refresh_token_json = {refresh_token_json}')

            # Fill in the missing data.
            refresh_token_json['refresh_token'] = refresh_token

            # Update the session
            updated_session = self._convert_token_response_to_session(refresh_token_json)
            self._session_store.save(self.session_id, updated_session)

            return updated_session
        else:
            error_msg = f"Unable to refresh tokens"

            try:
                error_json = refresh_token_res.json()
                error_msg += f": {error_json['error_description']}"
            except JSONDecodeError:
                pass

            raise RefreshException(auth_info.resource_url, error_msg)

    @staticmethod
    def _convert_token_response_to_session(response):
        assert 'access_token' in response, f'Failed to exchange tokens due to an unexpected response ({response})'

        created_time = time()
        expiry_time = created_time + response['expires_in']

        return Session(
            access_token=response['access_token'],
            refresh_token=response.get('refresh_token'),
            scope=response.get('scope'),
            token_type=response['token_type'],
            issued_at=created_time,
            valid_until=expiry_time,
        )


class ClientCredentialsAuth(OAuthTokenAuth):
    @property
    def grant_type(self):
        return 'client_credentials'

    def create_session(self, request_url: str, **kwargs) -> Session:
        auth_info = self._endpoint.authentication.oauth2
        response = requests.post(
            auth_info.token_endpoint,
            params=dict(
                client_id=auth_info.client_id,
                client_secret=auth_info.client_secret,
                grant_type=self.grant_type,
                resource=auth_info.resource_url,
            )
        )

        self._logger.debug(f'Response (RAW): {response.text}')

        if not response.ok:
            raise AuthException(msg=f'HTTP {response.status_code}: {response.text}',
                                service_type=self._endpoint.adapter_type,
                                url=request_url)

        return self._convert_token_response_to_session(response.json())

    def assert_auth_readiness(self):
        property_names = [
            'client_id',
            'client_secret',
            'grant_type',
            'resource_url',
            'token_endpoint',
        ]

        auth = self._auth_info

        missing_property_names = [
            property_name
            for property_name in property_names
            if not hasattr(auth, property_name) or not getattr(auth, property_name)
        ]

        if missing_property_names:
            raise InsufficientAuthInfoError(', '.join(missing_property_names))


class PersonalAccessTokenAuth(OAuthTokenAuth):
    """
    A Service Client authorization method using a personal access token (PAT)
    """

    def create_session(self, request_url: str, **kwargs) -> Session:
        oauth_response = self.__token_exchange()
        # Response Structure:
        #   access_token: str
        #   expires_in: int
        #   refresh_token: str
        #   scope: str
        #   token_type: str

        try:
            return self._convert_token_response_to_session(oauth_response)
        except AssertionError:
            raise AuthException(request_url)

    def assert_auth_readiness(self):
        property_names = [
            'authorization_endpoint',
            'client_id',
            'client_secret',
            'grant_type',
            'personal_access_endpoint',
            'personal_access_email',
            'personal_access_token',
            'redirect_url',
            'resource_url',
            'token_endpoint',
        ]

        auth = self._auth_info

        missing_property_names = [
            property_name
            for property_name in property_names
            if not hasattr(auth, property_name) or not getattr(auth, property_name)
        ]

        if missing_property_names:
            raise InsufficientAuthInfoError(', '.join(missing_property_names))

    def __token_exchange(self) -> Dict[AnyStr, Any]:
        session = requests.Session()

        info = self._auth_info

        self._logger.debug(f'Authenticating with PAT...')

        login_params = dict(token=info.personal_access_token,
                            email=info.personal_access_email)

        if in_global_debug_mode:
            self._logger.debug(f'login_params = {login_params}')

        login_url = info.personal_access_endpoint
        login_res = session.get(login_url,
                                params=dict(token=info.personal_access_token,
                                            email=info.personal_access_email),
                                allow_redirects=False)

        if not login_res.ok:
            session.close()
            raise LoginException(login_url, "The personal access token and/or email provided is invalid")

        self._logger.debug(f'Making an auth code challenge...')
        auth_code_url = info.authorization_endpoint
        auth_code_params = {
            "response_type": "code",
            "client_id": info.client_id,
            "resource": info.resource_url,
            "redirect_uri": info.redirect_url,
        }

        if info.scope:
            auth_code_params['scope'] = info.scope

        if in_global_debug_mode:
            self._logger.debug(f'auth_code_params = {auth_code_params}')

        auth_code_res = session.get(info.authorization_endpoint, params=auth_code_params, allow_redirects=False)

        auth_code_redirect_url = auth_code_res.headers["Location"]
        if "Location" in auth_code_res.headers:
            parsed_auth_code_redirect_url = urlparse(auth_code_redirect_url)
        else:
            session.close()
            raise LoginException(url=auth_code_url, msg="Authorization failed")

        query_params = parse_qs(parsed_auth_code_redirect_url.query)
        auth_code = self.__extract_code(auth_code_redirect_url)
        if parsed_auth_code_redirect_url.path.startswith('/oauth/confirm_access'):
            # Wait for a few seconds to give a chance to the user to abort the pre-authorization process.
            self._logger.warning('The access has not been authorized. Will automatically attempt to pre-authorize the '
                                 'access in 10 seconds.\n\nYou may press CTRL+C to abort the process')
            try:
                sleep(10)
            except KeyboardInterrupt:
                raise LoginException(url=auth_code_url, msg='User aborted the authentication process')
            confirm_prompt_response = session.get(auth_code_redirect_url)

            # Automatically authorize the access
            doc = BeautifulSoup(confirm_prompt_response.text, features="html.parser")
            form_element = [f for f in doc.find_all('form') if f.get('action').startswith('/oauth/confirm_access')][0]
            confirm_url: str = form_element.get('action')
            if not confirm_url.startswith('https://'):
                confirm_url = urljoin(info.token_endpoint, confirm_url)
            inputs = {
                input_element.get('name'): input_element.get('value')
                for input_element in form_element.find_all('input')
            }

            # Initiate the access confirmation response
            confirm_response = session.post(confirm_url, params=inputs, allow_redirects=False)
            if "Location" in confirm_response.headers:
                post_confirm_redirect_url = confirm_response.headers['Location']
            else:
                session.close()
                raise LoginException(url=auth_code_url, msg="Authorization failed (access confirmation failure)")

            post_confirm_code = self.__extract_code(post_confirm_redirect_url)
            if post_confirm_code:
                auth_code = query_params["code"][0]
            else:
                session.close()
                raise LoginException(url=auth_code_url, msg="Authorization failed (after access confirmation)")
        elif auth_code is None:
            session.close()
            raise LoginException(url=auth_code_url, msg="Authorization failed (no access confirmation)")

        self._logger.debug(f'Making a token exchange...')

        token_url = info.token_endpoint

        authorization_code_params = {
            "grant_type": info.grant_type,
            "code": auth_code,
            "resource": info.resource_url,
            "client_id": info.client_id,
            "client_secret": info.client_secret,
        }

        if info.scope:
            authorization_code_params['scope'] = info.scope

        if in_global_debug_mode:
            self._logger.debug(f'authorization_code_params = {authorization_code_params}')

        auth_token_res = requests.post(token_url, data=authorization_code_params)
        auth_token_json = auth_token_res.json()

        if in_global_debug_mode:
            self._logger.debug(f'Done: {auth_token_res.text}')

        session.close()

        if not auth_token_res.ok:
            raise LoginException(token_url, "Failed to get a token from the token endpoint")

        return auth_token_json

    @staticmethod
    def __extract_code(url: str):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if "code" in query_params and query_params["code"]:
            return query_params["code"][0]
        else:
            return None


class DeviceCodeAuth(OAuthTokenAuth):
    """
    A Service Client authorization method using the OAuth Device Code method
    """

    @property
    def grant_type(self):
        return 'urn:ietf:params:oauth:grant-type:device_code'

    def create_session(self, request_url: str, **kwargs) -> Session:
        oauth_response = self.__exchange_token(**kwargs)
        # Response Structure:
        #   access_token: str
        #   expires_in: int
        #   refresh_token: str
        #   scope: str
        #   token_type: str

        try:
            return self._convert_token_response_to_session(oauth_response)
        except AssertionError as e:
            raise AuthException(request_url, e)

    def assert_auth_readiness(self):
        property_names = [
            'client_id',
            'client_secret',
            'device_code_endpoint',
            'grant_type',
            'resource_url',
            'token_endpoint',
        ]

        auth = self._auth_info

        missing_property_names = [
            property_name
            for property_name in property_names
            if not hasattr(auth, property_name) or not getattr(auth, property_name)
        ]

        if missing_property_names:
            raise InsufficientAuthInfoError(', '.join(missing_property_names))

    def __exchange_token(self, open_browser: bool = False) -> Dict[str, Any]:
        """
        Generate an access token for a service using the Device Code flow

        :param audience: The service url(s) to authorize
        :param oauth_client: The authorization parameters of the service to be authorized.
        :param open_browser: Open a browser window automatically to the auth server. If this is False, the user must
            follow a returned url to authorize
        :return: A dict containing the OAuth access token as well as an expiry and a refresh token
        """
        session = requests.Session()
        grant_type = self._auth_info.grant_type
        login_url = self._auth_info.device_code_endpoint
        resource_url = self._auth_info.resource_url
        client_id = self._auth_info.client_id

        if grant_type != self.grant_type:
            raise LoginException(resource_url, f'Invalid Grant Type (expected: {self.grant_type})')

        if not login_url:
            raise LoginException(resource_url, "There is no device code url specified")

        device_code_res = session.post(
            login_url,
            params={
                "grant_type": self._auth_info.grant_type,
                "client_id": client_id,
                "resource": resource_url,
            },
            allow_redirects=False,
        )

        device_code_json = device_code_res.json()
        if in_global_debug_mode:
            self._logger.debug(f'Response from {login_url}:\n{pformat(device_code_json, indent=2)}')

        if device_code_res.ok:
            device_code = device_code_json["device_code"]
            device_verify_uri = device_code_json["verification_uri_complete"]
            poll_interval = int(device_code_json["interval"])
            expiry = time() + int(device_code_json["expires_in"])

            if open_browser:
                print(f"Opening {device_verify_uri} in your default browser")
                webbrowser.open(device_verify_uri, new=2)
            else:
                print(f"Please go to {device_verify_uri} to continue.")
        else:
            if "error" in device_code_res.json():
                error_message = f'The device code request failed with message "{device_code_json["error"]}"'
            else:
                error_message = "The device code request failed"

            raise LoginException(url=login_url, msg=error_message)

        token_url = self._auth_info.token_endpoint

        while time() < expiry:
            auth_token_res = session.post(
                token_url,
                data={
                    "grant_type": self.grant_type,
                    "device_code": device_code,
                    "client_id": client_id,
                },
            )

            auth_token_json = auth_token_res.json()
            if in_global_debug_mode:
                self._logger.debug(f'Response from {token_url}:\n{pformat(auth_token_json, indent=2)}')

            if auth_token_res.ok:
                session.close()
                return auth_token_json
            elif "error" in auth_token_json:
                if auth_token_json.get("error") == "authorization_pending":
                    sleep(poll_interval)
                    continue
                error_msg = "Failed to retrieve a token"
                if "error_description" in auth_token_json:
                    error_msg += f": {auth_token_json['error_description']}"
                raise LoginException(url=token_url, msg=error_msg)

            sleep(poll_interval)

        raise LoginException(url=token_url, msg="The authorize step timed out.")


# TODO Remove this class in v3.0
class RefreshTokenAuth(OAuthTokenAuth):
    """
    A Service Client authorization method using the OAuth Refresh Token method

    :param refresh_token: An OAuth Refresh Token to authorize the user
    :param oauth_client: The :class:`OAuthClientParams` to authorize the user with.
    """

    def create_session(self, request_url: str, **kwargs) -> Session:
        if not self._oauth_client:
            raise AuthException(request_url, "There is no OAuth Client configured")
        oauth_response = login_refresh_token(
            token=self.refresh_token,
            oauth_client=self._oauth_client,
        )
        if oauth_response.get("access_token"):
            # oauth_response["issuer"] = self._oauth_client.base_url
            oauth_response["expiry"] = time() + oauth_response.get("expires_in")
            return oauth_response
        else:
            raise AuthException(request_url, "Unable to retrieve access token using Refresh Token")

    def assert_auth_readiness(self):
        # Nothing to assert here.
        pass


class AwsSigv4Auth(AuthBase):
    def __init__(self, endpoint: ServiceEndpoint):
        super().__init__()
        self._endpoint = endpoint
        self._logger = get_logger(f'{endpoint.adapter_type}/{endpoint.id}')
        self._session_store: SessionStore = container.get(SessionStore)
        self._session: Optional[Session] = None

    def __call__(self, r):
        """
        Adds the authorization headers required by Amazon's signature
        version 4 signing process to the request.
        Adapted from https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
        """
        aws_headers = self.get_aws_request_headers_handler(r)
        r.headers.update(aws_headers)
        return r

    @property
    def _auth_info(self) -> AwsAuthentication:
        return self._endpoint.authentication.aws

    def assert_auth_readiness(self):
        property_names = [
            "access_key_id",
            "access_key_secret",
            "host",
            "region",
            "service"
        ]
        auth = self._auth_info

        missing_property_names = [
            property_name
            for property_name in property_names
            if not hasattr(auth, property_name) or not getattr(auth, property_name)
        ]

        if missing_property_names:
            raise InsufficientAuthInfoError(', '.join(missing_property_names))

    def get_aws_request_headers_handler(self, r):
        """
        Override get_aws_request_headers_handler() if you have a
        subclass that needs to call get_aws_request_headers() with
        an arbitrary set of AWS credentials. The default implementation
        calls get_aws_request_headers() with self.aws_access_key,
        self.aws_secret_access_key, and self.aws_token
        """
        self.assert_auth_readiness()
        return self.get_aws_request_headers(r=r,
                                            aws_access_key=self._auth_info.access_key_id,
                                            aws_secret_access_key=self._auth_info.access_key_secret,
                                            aws_token=self._auth_info.token)

    def get_aws_request_headers(self, r, aws_access_key, aws_secret_access_key, aws_token):
        """
        Returns a dictionary containing the necessary headers for Amazon's
        signature version 4 signing process. An example return value might
        look like
            {
                'Authorization': 'AWS4-HMAC-SHA256 Credential=YOURKEY/20160618/us-east-1/es/aws4_request, '
                                 'SignedHeaders=host;x-amz-date, '
                                 'Signature=ca0a856286efce2a4bd96a978ca6c8966057e53184776c0685169d08abd74739',
                'x-amz-date': '20160618T220405Z',
            }
        """
        # Create a date for headers and the credential string
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d')  # Date w/o time for credential_scope

        canonical_uri = AwsSigv4Auth.get_canonical_path(r)

        canonical_querystring = AwsSigv4Auth.get_canonical_querystring(r)

        # Create the canonical headers and signed headers. Header names
        # and value must be trimmed and lowercase, and sorted in ASCII order.
        # Note that there is a trailing \n.
        canonical_headers = ('host:' + self._auth_info.host + '\n' +
                             'x-amz-date:' + amzdate + '\n')
        if aws_token:
            canonical_headers += 'x-amz-security-token:' + aws_token + '\n'

        # Create the list of signed headers. This lists the headers
        # in the canonical_headers list, delimited with ";" and in alpha order.
        # Note: The request can include any headers; canonical_headers and
        # signed_headers lists those that you want to be included in the
        # hash of the request. "Host" and "x-amz-date" are always required.
        signed_headers = 'host;x-amz-date'
        if aws_token:
            signed_headers += ';x-amz-security-token'

        # Materialize body if it is a generator (e.g. toolbelt's MultipartEncoder instance)
        if r.body and hasattr(r.body, 'to_string'):
            r.body = r.body.to_string()

        # Create payload hash (hash of the request body content). For GET
        # requests, the payload is an empty string ('').
        body = r.body if r.body else bytes()
        try:
            body = body.encode('utf-8')
        except (AttributeError, UnicodeDecodeError):
            # On py2, if unicode characters in present in `body`,
            # encode() throws UnicodeDecodeError, but we can safely
            # pass unencoded `body` to execute hexdigest().
            #
            # For py3, encode() will execute successfully regardless
            # of the presence of unicode data
            body = body

        payload_hash = hashlib.sha256(body).hexdigest()

        # Combine elements to create create canonical request
        canonical_request = (r.method + '\n' + canonical_uri + '\n' +
                             canonical_querystring + '\n' + canonical_headers +
                             '\n' + signed_headers + '\n' + payload_hash)

        # Match the algorithm to the hashing algorithm you use, either SHA-1 or
        # SHA-256 (recommended)
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = (datestamp + '/' + self._auth_info.region + '/' +
                            self._auth_info.service + '/' + 'aws4_request')
        string_to_sign = (algorithm + '\n' + amzdate + '\n' + credential_scope +
                          '\n' + hashlib.sha256(canonical_request.encode('utf-8')).hexdigest())

        # Create the signing key using the function defined above.
        signing_key = AwsSigv4Auth.get_signature_key(key=aws_secret_access_key,
                                                     dateStamp=datestamp,
                                                     regionName=self._auth_info.region,
                                                     serviceName=self._auth_info.service)

        # Sign the string_to_sign using the signing_key
        string_to_sign_utf8 = string_to_sign.encode('utf-8')
        signature = hmac.new(signing_key,
                             string_to_sign_utf8,
                             hashlib.sha256).hexdigest()

        # The signing information can be either in a query string value or in
        # a header named Authorization. This code shows how to use a header.
        # Create authorization header and add to request headers
        authorization_header = (algorithm + ' ' + 'Credential=' + aws_access_key +
                                '/' + credential_scope + ', ' + 'SignedHeaders=' +
                                signed_headers + ', ' + 'Signature=' + signature)

        headers = {
            'Authorization': authorization_header,
            'x-amz-date': amzdate,
            'x-amz-content-sha256': payload_hash
        }
        if aws_token:
            headers['X-Amz-Security-Token'] = aws_token
        return headers

    @classmethod
    def get_canonical_path(cls, r):
        """
        Create canonical URI--the part of the URI from domain to query
        string (use '/' if no path)
        """
        parsedurl = urlparse(r.url)

        # safe chars adapted from boto's use of urllib.parse.quote
        # https://github.com/boto/boto/blob/d9e5cfe900e1a58717e393c76a6e3580305f217a/boto/auth.py#L393
        return quote(parsedurl.path if parsedurl.path else '/', safe='/-_.~')

    @classmethod
    def get_canonical_querystring(cls, r):
        """
        Create the canonical query string. According to AWS, by the
        end of this function our query string values must
        be URL-encoded (space=%20) and the parameters must be sorted
        by name.
        This method assumes that the query params in `r` are *already*
        url encoded.  If they are not url encoded by the time they make
        it to this function, AWS may complain that the signature for your
        request is incorrect.
        It appears elasticsearc-py url encodes query paramaters on its own:
            https://github.com/elastic/elasticsearch-py/blob/5dfd6985e5d32ea353d2b37d01c2521b2089ac2b/elasticsearch/connection/http_requests.py#L64
        If you are using a different client than elasticsearch-py, it
        will be your responsibility to urleconde your query params before
        this method is called.
        """
        canonical_querystring = ''

        parsedurl = urlparse(r.url)
        querystring_sorted = '&'.join(sorted(parsedurl.query.split('&')))

        for query_param in querystring_sorted.split('&'):
            key_val_split = query_param.split('=', 1)

            key = key_val_split[0]
            if len(key_val_split) > 1:
                val = key_val_split[1]
            else:
                val = ''

            if key:
                if canonical_querystring:
                    canonical_querystring += "&"
                canonical_querystring += u'='.join([key, val])

        return canonical_querystring

    @classmethod
    def sign(cls, key, msg):
        """
        Copied from https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
        """
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    @classmethod
    def get_signature_key(cls, key, dateStamp, regionName, serviceName):
        """
        Copied from https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
        """
        kDate = AwsSigv4Auth.sign(('AWS4' + key).encode('utf-8'), dateStamp)
        kRegion = AwsSigv4Auth.sign(kDate, regionName)
        kService = AwsSigv4Auth.sign(kRegion, serviceName)
        kSigning = AwsSigv4Auth.sign(kService, 'aws4_request')
        return kSigning
