from time import time

from datetime import date
from json import JSONDecodeError

import json
import os.path
from typing import Dict

import shutil

import subprocess

from click.testing import CliRunner, Result

from dnastack.__main__ import dnastack as cli_app
from dnastack.helpers.environments import env, flag
from dnastack.helpers.logger import get_logger
from dnastack.tests.exam_helper import ReversibleTestCase, ExtendedBaseTestCase


class CliTestCase(ReversibleTestCase, ExtendedBaseTestCase):
    _runner = CliRunner(mix_stderr=False)
    _debug = flag('DNASTACK_DEBUG')
    _config_file_path = env('DNASTACK_CONFIG_FILE')
    _session_dir_path = env('DNASTACK_SESSION_DIR')
    _config_overriding_allowed = flag('E2E_CONFIG_OVERRIDING_ALLOWED')

    def __init__(self, *args, **kwargs):
        super(CliTestCase, self).__init__(*args, **kwargs)
        self._logger = get_logger(f'{type(self).__name__}')

    def setUp(self) -> None:
        super().setUp()
        self._reset_session()
        self._temporarily_remove_existing_config()

    def tearDown(self) -> None:
        super().tearDown()
        self._reset_session()
        self._restore_existing_config()

    @staticmethod
    def execute(command: str):
        """ Execute a shell script via subprocess directly.

            This is for debugging only. Please use :method:`invoke` for testing.
        """
        subprocess.call(command, shell=True)

    def invoke(self, *cli_blocks: str, bypass_error: bool = False) -> Result:
        # noinspection PyTypeChecker
        result = self._runner.invoke(cli_app, cli_blocks)
        if result.exception and not bypass_error:
            raise result.exception
        return result

    def simple_invoke(self, *cli_blocks: str):
        result = self.invoke(*cli_blocks, bypass_error=False)
        self.assertEqual(0, result.exit_code,
                         'The command "' + (' '.join(cli_blocks)) + f'" returns the exit code {result.exit_code}')
        return self.parse_json(result.output)

    @staticmethod
    def parse_json(json_string: str):
        try:
            return json.loads(json_string)
        except JSONDecodeError:
            raise ValueError(f'Unable to parse this JSON string:\n\n{json_string}')

    def _configure(self, config: Dict[str, str]):
        for k, v in config.items():
            self.invoke('config', 'set', k, v)

    def _temporarily_remove_existing_config(self):
        backup_path = self._config_file_path + '.backup'
        if os.path.exists(self._config_file_path):
            self._logger.debug(f"Detected the existing configuration file {self._config_file_path}.")
            if self._config_overriding_allowed:
                self._logger.debug(f"Temporarily moving {self._config_file_path} to {backup_path}...")
                shutil.copy(self._config_file_path, backup_path)
                os.unlink(self._config_file_path)
                self._logger.debug(f"Successfully moved {self._config_file_path} to {backup_path}.")
            else:
                raise RuntimeError(f'{self._config_file_path} already exists. Please define DNASTACK_CONFIG_FILE ('
                                   f'environment variable) to a different location or E2E_CONFIG_OVERRIDING_ALLOWED ('
                                   f'environment variable) to allow the test to automatically backup the existing '
                                   f'test configuration.')

    def _restore_existing_config(self):
        backup_path = self._config_file_path + '.backup'
        if os.path.exists(backup_path):
            self._logger.debug(f"Restoring {self._config_file_path}...")
            shutil.copy(backup_path, self._config_file_path)
            os.unlink(backup_path)
            self._logger.debug(f"Successfully restored {self._config_file_path}.")

    def _reset_session(self):
        if os.path.exists(self._session_dir_path):
            self._logger.debug("Removing the test session directory...")
            self.execute(f'rm -r{"v" if self._debug else ""} {self._session_dir_path}')
            self._logger.debug("Removed the test session directory.")

import json
import unittest
from json import JSONDecodeError
from typing import AnyStr, List, Union, Pattern, Dict, Any

from click.testing import CliRunner

from .utils import clear_config
from ...__main__ import dnastack as cli
from ...auth import OAuthClientParams


class BaseCliTestCase(unittest.TestCase):
    runner = CliRunner(mix_stderr=False)

    def __init__(self, *args, **kwargs):
        self.files = []
        super().__init__(*args, **kwargs)

    def skip_until(self, iso_date_string: str):
        expiry_time = date.fromisoformat(iso_date_string)
        current_time = date.fromtimestamp(time())

        if (current_time - expiry_time).days > 0:
            self.fail("This test requires your attention.")
        else:
            self.skipTest(f"This test will be skipped until {iso_date_string}.")

    def setUp(self) -> None:
        # FIXME [#180837771] Back up user's configuration and restore it when necessary.
        clear_config()
        self.setUpCLI()

    def setUpCLI(self):
        pass

    def assertCommand(
        self,
        command: List[AnyStr],
        exit_code: int = 0,
        json_output: bool = False,
        has_keys: List[AnyStr] = None,
        has_list_of_keys: List[AnyStr] = None,
        output_pattern: Union[Pattern[AnyStr], AnyStr] = None,
    ) -> Union[Dict[AnyStr, Any], AnyStr, None]:
        result = self.runner.invoke(cli, ["--debug"] + command)

        self.assertEqual(
            result.exit_code,
            exit_code,
            f"[dnastack {' '.join([str(c) for c in command])}] "
            f"{'succeeded' if exit_code else 'failed'} "
            f"unexpectedly, expected exit code [{exit_code}],"
            f" got [{result.exit_code}], output: {result.output}",
        )

        if output_pattern:
            self.assertRegex(result.output, output_pattern)

        if json_output:
            try:
                out = json.loads(result.output)

                if has_keys:
                    for key in has_keys:
                        self.assertIn(
                            key,
                            out.keys(),
                            f"Cannot find key [{key}] in the JSON output of "
                            f"{' '.join([str(c) for c in command])}. \n"
                            f"(output: {json.dumps(out)})",
                        )
                elif has_list_of_keys:
                    for item in out:
                        for key in has_list_of_keys:
                            self.assertIn(
                                key,
                                item.keys(),
                                f"Cannot find key [{key}] in an item of the JSON output of "
                                f"{' '.join([str(c) for c in command])}. \n"
                                f"(output: {json.dumps(out, indent=4)}) \n"
                                f"(item: {json.dumps(item, indent=4)})",
                            )

            except JSONDecodeError as j:
                self.fail(
                    f"Unable to parse output as JSON for command [{' '.join(command)}] (output: {result.output})"
                )
        else:
            out = result.output

        return out

    def get_config(self, key: AnyStr, **kwargs):
        result = self.assertCommand(["config", "get", key], **kwargs)
        return result

    def set_config(self, key: AnyStr, value: Any):
        self.assertCommand(["config", "set", key, value])

    def define_oauth_client(self, service: AnyStr, oauth_client: OAuthClientParams):
        self.set_config(f"{service}.auth.url", oauth_client.base_url)
        self.set_config(f"{service}.auth.token_url", oauth_client.token_url)
        self.set_config(
            f"{service}.auth.authorization_url", oauth_client.authorization_url
        )
        self.set_config(f"{service}.auth.device_code_url", oauth_client.device_code_url)
        self.set_config(f"{service}.auth.client.id", oauth_client.client_id)
        self.set_config(f"{service}.auth.client.secret", oauth_client.client_secret)
        self.set_config(
            f"{service}.auth.client.redirect_url", oauth_client.client_redirect_url
        )
        self.set_config(f"{service}.auth.client.scope", oauth_client.scope)

    def define_refresh_token(self, service: AnyStr, refresh_token: AnyStr):
        self.set_config(f"{service}.auth.refresh_token", refresh_token)

    def define_personal_access_token(self, service: AnyStr, email: AnyStr, personal_access_token: AnyStr):
        self.set_config(f"{service}.auth.email", email)
        self.set_config(f"{service}.auth.personal_access_token", personal_access_token)

    def define_service_registry(self, service_registry: AnyStr):
        self.set_config("service_registry.url", service_registry)
