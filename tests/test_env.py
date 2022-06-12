import logging
import unittest
from env import ALICE_PK, Env, DEFAULT_BAKER

logging.basicConfig(level=logging.INFO)


class TestEnv(unittest.TestCase):

    def test_deploy_full_app(self):
        factory, smak_token, sink, _ = Env().deploy_full_app(DEFAULT_BAKER, ALICE_PK)
        self.assertEqual(factory.storage["default_smak_token_type"](), {
                         "fa12": smak_token.address})
        self.assertEqual(factory.storage["default_sink"](), sink.address)
        self.assertEqual(sink.storage["factory_address"](), factory.address)


if __name__ == "__main__":
    unittest.main()
