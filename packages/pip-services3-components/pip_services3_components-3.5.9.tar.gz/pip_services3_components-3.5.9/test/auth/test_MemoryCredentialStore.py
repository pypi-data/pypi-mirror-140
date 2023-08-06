# -*- coding: utf-8 -*-
from pip_services3_commons.config import ConfigParams
from pip_services3_components.auth import MemoryCredentialStore

from pip_services3_components.auth.CredentialParams import CredentialParams


class TestMemoryCredentialStore:

    def test_lookup_and_store(self):
        config = ConfigParams.from_tuples(
            'key1.user', 'user1',
            'key1.pass', 'pass1',
            'key2.user', 'user2',
            'key2.pass', 'pass2'
        )

        credential_store = MemoryCredentialStore()
        credential_store.read_credentials(config)

        cred1 = credential_store.lookup('123', 'key1')
        cred2 = credential_store.lookup('123', 'key2')

        assert cred1.get_username() == 'user1'
        assert cred1.get_password() == 'pass1'
        assert cred2.get_username() == 'user2'
        assert cred2.get_password() == 'pass2'

        cred_config = CredentialParams.from_tuples(
            'user', 'user3',
            'pass', 'pass3',
            'access_id', '123'
        )

        credential_store.store(None, 'key3', cred_config)

        cred3 = credential_store.lookup('123', 'key3')

        assert cred3.get_username() == 'user3'
        assert cred3.get_password() == 'pass3'
        assert cred3.get_access_id() == '123'
