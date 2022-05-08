import unittest
from env import Env, FA12Storage, FA2Storage, FactoryStorage, LqtStorage, ALICE_PK

import logging
logging.basicConfig(level=logging.INFO)


class TestEnv(unittest.TestCase):
    def test_deploy_fa2(self):
        init_storage = FA2Storage()
        fa2 = Env().deploy_fa2(init_storage)

        self.assertEqual(fa2.storage["administrator"](), ALICE_PK)

    def test_deploy_fa12(self):
        init_storage = FA12Storage(ALICE_PK)
        fa12 = Env().deploy_fa12(init_storage)

        self.assertEqual(fa12.storage["admin"](), ALICE_PK)

    def test_deploy_factory(self):
        init_storage = FactoryStorage()
        factory = Env().deploy_factory(init_storage)

    def test_deploy_liquidity_token(self):
        init_storage = LqtStorage()
        lqt = Env().deploy_liquidity_token(init_storage)

    def test_deploy_full_app(self):
        factory, smak_token, sink, multisig = Env().deploy_full_app()
        self.assertEqual(factory.storage["default_smak_token_type"](), {
                         "fa12": smak_token.address})
        self.assertEqual(factory.storage["default_sink"](), sink.address)
        self.assertEqual(sink.storage["factory_address"](), factory.address)


if __name__ == "__main__":
    unittest.main()
