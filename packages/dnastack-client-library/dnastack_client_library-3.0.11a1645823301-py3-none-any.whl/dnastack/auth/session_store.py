from json import loads
from threading import Lock

from typing import Optional, Dict

from time import time

import shutil

import os
from cryptography.fernet import Fernet

from imagination.decorator import service, EnvironmentVariable
from pydantic import BaseModel

from dnastack.constants import CLI_DIRECTORY


class Session(BaseModel):
    version: int = 3
    access_token: Optional[str]
    refresh_token: Optional[str]
    scope: Optional[str]
    token_type: str

    # Pre-computed Properties
    issued_at: int  # Epoch timestamp (UTC)
    valid_until: int  # Epoch timestamp (UTC)

    def is_valid(self) -> bool:
        return time() <= self.valid_until


class UnknownSessionError(RuntimeError):
    """ Raised when an unknown session is requested """


@service.registered(
    params=[
        EnvironmentVariable('DNASTACK_SESSION_DIR',
                            default=os.path.join(CLI_DIRECTORY, 'sessions'),
                            allow_default=True),
        EnvironmentVariable('DNASTACK_SESSION_ENCRYPTED',
                            parse_value=lambda x: (x.lower() in ['1', 'true']) if x else False,
                            default=False,
                            allow_default=True)
    ]
)
class SessionStore:
    def __init__(self, dir_path : str, encryption_enabled: bool = False):
        self.__dir_path = dir_path
        self.__encryption_enabled = encryption_enabled
        self.__file_locks: Dict[str, Lock] = dict()

        if not os.path.exists(self.__dir_path):
            os.makedirs(self.__dir_path, exist_ok=True)

        # FIXME Get from the system keyring.
        self.__cryptographic_key = b'0h_sN1UuI5xCV918_5i5MmluE7TyRY9WjhbsbgBeCEw='
        self.__cryptographer = Fernet(self.__cryptographic_key)

    def restore(self, id: str) -> Optional[Session]:
        final_file_path = os.path.join(self.__dir_path, f'{id}.session')

        if not os.path.exists(final_file_path):
            return None

        with self.__lock(id):
            with open(final_file_path, 'r') as f:
                content = f.read()

        if self.__encryption_enabled:
            content = self.__cryptographer.decrypt(content.encode())

        raw_session = loads(content)

        return Session(**raw_session)

    def save(self, id: str, session: Session):
        # Note (1): This is designed to have file operation done as quickly as possible to reduce race conditions.
        # Note (2): Instead of interfering with the main file directly, the new content is written to a temp file before
        #           swapping with the real file to minimize the I/O block.
        os.makedirs(self.__dir_path, exist_ok=True)

        final_file_path = os.path.join(self.__dir_path, f'{id}.session')
        temp_file_path = f'{final_file_path}.{time()}.swap'

        content: str = session.json(indent=0 if self.__encryption_enabled else 2)

        if self.__encryption_enabled:
            encrypted_content = self.__cryptographer.encrypt(content.encode())
            content = encrypted_content.decode()

        with self.__lock(id):
            with open(temp_file_path, 'w') as f:
                f.write(content)
            shutil.copy(temp_file_path, final_file_path)
            os.unlink(temp_file_path)

    def delete(self, id: str):
        final_file_path = os.path.join(self.__dir_path, f'{id}.session')
        with self.__lock(id):
            if not os.path.exists(final_file_path):
                return
            os.unlink(final_file_path)

    def __lock(self, id) -> Lock:
        if id not in self.__file_locks:
            self.__file_locks[id] = Lock()
        return self.__file_locks[id]
