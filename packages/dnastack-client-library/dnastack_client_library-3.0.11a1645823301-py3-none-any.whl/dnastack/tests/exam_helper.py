from datetime import date
from threading import Lock

from typing import Callable, List, Optional
from unittest import TestCase

from time import time, sleep

from contextlib import contextmanager

from urllib.parse import urljoin
from uuid import uuid4

from dnastack.configuration import ServiceEndpoint, Authentication, Oauth2Authentication
from dnastack.helpers.environments import env
from dnastack.helpers.logger import get_logger

client_id = env('E2E_CLIENT_ID', required=True)
client_secret = env('E2E_CLIENT_SECRET', required=True)

wallet_url = env('E2E_WALLET_BASE_URL', required=True)
passport_url = env('E2E_PASSPORT_BASE_URL', default=wallet_url)
redirect_url = env('E2E_REDIRECT_URL', default=wallet_url)

authorization_endpoint = urljoin(wallet_url, '/oauth/authorize')
device_code_endpoint = urljoin(wallet_url, '/oauth/device/code')
personal_access_endpoint = urljoin(passport_url, '/login/token')
token_endpoint = urljoin(wallet_url, '/oauth/token')


def initialize_test_endpoint(service_type: str, resource_url: str, secure: bool = True) -> ServiceEndpoint:
    auth_info = Authentication(
        oauth2=Oauth2Authentication(
            client_id=client_id,
            client_secret=client_secret,
            grant_type='client_credentials',
            resource_url=resource_url,
            token_endpoint=token_endpoint,
        )
    ) if secure else None

    return ServiceEndpoint(
        id=f'auto-test-{uuid4()}',
        adapter_type=service_type,
        url=resource_url,
        authentication=auth_info,
        mode=env('E2E_CLIENT_MODE', default='standard', required=False),
    )


@contextmanager
def measure_runtime(description: str, log_level: str = None):
    _logger = get_logger('timer')
    log_level = log_level or 'debug'
    start_time = time()
    yield
    getattr(_logger, log_level)(f'{description} ({time() - start_time:.3f}s)')


class CallableProxy():
    def __init__(self, operation: Callable, args, kwargs):
        self.operation = operation
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        self.operation(*self.args, **self.kwargs)


class ReversibleTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(ReversibleTestCase, self).__init__(*args, **kwargs)
        self._revert_operation_lock = Lock()
        self._revert_operations: List[CallableProxy] = list()

    def after_this_test(self, operation: Callable, *args, **kwargs):
        with self._revert_operation_lock:
            self._revert_operations.insert(0, CallableProxy(operation, args, kwargs))

    def tearDown(self) -> None:
        with self._revert_operation_lock:
            while self._revert_operations:
                revert_operation = self._revert_operations.pop(0)
                revert_operation()
            self._revert_operations.clear()


class ExtendedBaseTestCase(TestCase):
    def assert_not_empty(self, obj, message: Optional[str] = None):
        self.assertIsNotNone(obj, message)
        self.assertGreater(len(obj), 0, message)

    def skip_until(self, iso_date_string: str):
        expiry_time = date.fromisoformat(iso_date_string)
        current_time = date.fromtimestamp(time())

        if (current_time - expiry_time).days > 0:
            self.fail("This test requires your attention.")
        else:
            self.skipTest(f"This test will be skipped until {iso_date_string}.")

    # noinspection PyMethodMayBeStatic
    def retry_if_fail(self, test_operation: Callable, max_run_count: int = 3, intermediate_cleanup: Callable = None):
        current_run_count = max_run_count
        while True:
            current_run_count -= 1
            try:
                test_operation()
                break
            except Exception:
                if current_run_count > 0:
                    if intermediate_cleanup:
                        intermediate_cleanup()
                    sleep(10)
                    continue
                else:
                    raise RuntimeError(f'Still failed after {max_run_count} run(s)')
