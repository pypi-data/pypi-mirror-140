import re
import threading
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
from typing import Dict

from .base import CliTestCase
from .utils import *
from ..exam_helper import client_id, client_secret, token_endpoint, authorization_endpoint, personal_access_endpoint, \
    redirect_url, device_code_endpoint
from ...helpers.environments import env, flag


class TestAuthentication(CliTestCase):
    re_url = re.compile(r'https://[^\s]+')
    test_resource_url = env('E2E_PROTECTED_DATA_CONNECT_URL', default='https://data-connect-trino.viral.ai/')

    def setUp(self) -> None:
        super().setUp()
        self.invoke('config', 'set', 'data_connect.url', self.test_resource_url)

    def test_client_credentials_flow(self):
        self._configure({
            'data_connect.authentication.oauth2.client_id': client_id,
            'data_connect.authentication.oauth2.client_secret': client_secret,
            'data_connect.authentication.oauth2.grant_type': 'client_credentials',
            'data_connect.authentication.oauth2.resource_url': self.test_resource_url,
            'data_connect.authentication.oauth2.token_endpoint': token_endpoint,
        })
        # self.execute(f'cat {self._config_file_path}')
        result = self.invoke('auth', 'login', 'data_connect')
        self.assertEqual(0, result.exit_code)

    def test_personal_access_token_flow(self):
        email = env('E2E_AUTH_TEST_PAT_EMAIL')
        token = env('E2E_AUTH_TEST_PAT_TOKEN')

        if not email or not token:
            self.skipTest('The PAT flow test does not have both email and token.')

        self._configure({
            'data_connect.authentication.oauth2.authorization_endpoint': authorization_endpoint,
            'data_connect.authentication.oauth2.client_id': client_id,
            'data_connect.authentication.oauth2.client_secret': client_secret,
            'data_connect.authentication.oauth2.grant_type': 'authorization_code',
            'data_connect.authentication.oauth2.personal_access_endpoint': personal_access_endpoint,
            'data_connect.authentication.oauth2.personal_access_email': email,
            'data_connect.authentication.oauth2.personal_access_token': token,
            'data_connect.authentication.oauth2.redirect_url': redirect_url,
            'data_connect.authentication.oauth2.resource_url': self.test_resource_url,
            'data_connect.authentication.oauth2.token_endpoint': token_endpoint
        })
        # self.execute(f'cat {self._config_file_path}')
        result = self.invoke('auth', 'login', 'data_connect')
        self.assertEqual(0, result.exit_code)

    def test_device_code_flow(self):
        self.skip_until('2022-04-01')
        self._configure({
            'data_connect.authentication.oauth2.client_id': client_id,
            'data_connect.authentication.oauth2.client_secret': client_secret,
            'data_connect.authentication.oauth2.device_code_endpoint': device_code_endpoint,
            'data_connect.authentication.oauth2.grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'data_connect.authentication.oauth2.redirect_url': redirect_url,
            'data_connect.authentication.oauth2.resource_url': self.test_resource_url,
            'data_connect.authentication.oauth2.token_endpoint': token_endpoint
        })
        # self.execute(f'cat {self._config_file_path}')
        # result = self.invoke('auth', 'login', 'data_connect')
        # self.assertEqual(0, result.exit_code)

        self._logger.warning('Initiating the login process...')
        proc = subprocess.Popen(['python3', '-m', 'dnastack', 'auth', 'login', 'data_connect',
                                 '--no-browser', '--delay-init', '5'],
                                stdout=subprocess.PIPE)
        self._logger.warning('Initiated the login process.')

        shared_memory = dict()

        # self._logger.warning('Have a webdrive to follow up')
        # self.do_login_steps(proc, shared_memory)

        login_thread = threading.Thread(target=self.do_login_steps, args=(proc, shared_memory))
        self._logger.warning('Starting the webdriver thread...')
        login_thread.start()
        self._logger.warning('Waiting for the webdriver thread to join back...')
        login_thread.join()
        self._logger.warning('The webdriver thread joined back.')

        proc.wait(timeout=30)  # timeout = 30 seconds
        output, error = proc.communicate()
        exit_code = proc.returncode

        thread_error = shared_memory.get('error')
        if thread_error:
            self.fail(f'Unexpected exception: {thread_error}')

        self.assertEqual(
            exit_code,
            0,
            msg=f"Login failed with output: {output.decode('utf-8')} (exit code {exit_code})",
        )
        self.assertIn("login successful", output.decode("utf-8").lower())

    def do_login_steps(self, proc, memory: Dict[str, Any], allow=True):
        self._logger.warning('Initiated the login step')

        email = env('E2E_AUTH_TEST_PAT_EMAIL')
        token = env('E2E_AUTH_TEST_PAT_TOKEN')

        if not email or not token:
            self.skipTest('The test does not have both email and token.')

        # wait for device code url
        retries = 2
        output_buffer_list = []
        device_code_url = None

        sleep(5)

        while device_code_url is None:
            output_buffer = proc.stdout.read().decode("utf-8")
            output_buffer_list.append(output_buffer)

            self._logger.warning(f'PIPE: {output_buffer}')

            matches = TestAuthentication.re_url.search(output_buffer)

            if matches:
                device_code_url = matches.group(0)
                self._logger.warning('Detected the device code URL')
            else:
                retries -= 1
                self._logger.warning('Not yet detected the device code URL...')
                if retries < 0:
                    self._logger.warning('Not yet detected the device code URL but over the limit. Terminated')
                    output = '\n\t'.join(output_buffer_list)
                    memory['error'] = f'No possible device code URL found within the time limit:\n\t{output}\n***** ENDED *****\n'
                    return
                else:
                    sleep(1)

        self._logger.warning(f'Device Code URL: {device_code_url}')

        # make sure the browser is opened in headless mode
        chrome_options = Options()
        chrome_options.headless = flag('E2E_HEADLESS')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)

        self._logger.warning(f'Web driver: activated')

        driver.get(device_code_url)

        self._logger.warning(f'Web driver: Go to {device_code_url}')

        driver.execute_script(
            (
                f"document.querySelector('form[name=\"token\"] input[name=\"token\"]').value = '{email}';"
                f"document.querySelector('form[name=\"token\"] input[name=\"email\"]').value = '{token}';"
            )
        )

        sleep(5)
        self._logger.warning(f'Web driver: URL: {driver.current_url}')
        self._logger.warning(f'Web driver: URL: {driver.page_source}')

        token_form = driver.find_element(By.CSS_SELECTOR, "form[name='token']")
        token_form.submit()

        sleep(2)

        try:
            driver.find_element(By.ID, "continue-btn").click()

            if allow:
                driver.find_element(By.ID, "allow-btn").click()
            else:
                driver.find_element(By.ID, "deny-btn").click()
        except Exception as e:
            memory['error'] = str(e)
            self._logger.error(traceback.format_exc())
        finally:
            driver.quit()
