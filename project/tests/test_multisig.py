from env import Env, ALICE_PK, BOB_PK, pytezos, bob_pytezos, MultisigStorage, send_conf, CHARLIE_PK
from pytezos.rpc.errors import MichelsonError

import unittest

import logging
logging.basicConfig(level=logging.INFO)


class TestMultisig(unittest.TestCase):
    @staticmethod
    def print_title(instance):
        print("-----------------------------------")
        print("Test Multisig: " + instance.__class__.__name__ + "...")
        print("-----------------------------------")

    @staticmethod
    def print_start(function_name):
        print("-----------------------------------")
        print("running test: " + function_name)
        print("-----------------------------------")

    @staticmethod
    def print_success(function_name):
        print("-----------------------------------")
        print(function_name + "... ok")
        print("-----------------------------------")

    class AddAdmin(unittest.TestCase):
        def test01_it_adds_admin(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertNotIn(BOB_PK, multisig.storage["admins"]())
            multisig.addAdmin(BOB_PK).send(**send_conf)
            self.assertIn(BOB_PK, multisig.storage["admins"]())

        def test02_it_fails_when_caller_not_admin(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertNotIn(BOB_PK, multisig.storage["admins"]())
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(multisig.address).addAdmin(
                    BOB_PK).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1001"})

        def test03_it_fails_when_caller_votes_twice(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertNotIn(BOB_PK, multisig.storage["admins"]())
            multisig.addAdmin(
                BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            multisig.addAdmin(
                CHARLIE_PK).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                multisig.addAdmin(
                    CHARLIE_PK).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1008"})

    class AddAuthorizedContract(unittest.TestCase):
        def test01_it_adds_authorized_contract(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertNotIn(
                BOB_PK, multisig.storage["authorized_contracts"]())
            multisig.addAuthorizedContract(BOB_PK).send(**send_conf)
            self.assertIn(BOB_PK, multisig.storage["authorized_contracts"]())

        def test02_it_fails_when_caller_not_admin(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertNotIn(
                BOB_PK, multisig.storage["authorized_contracts"]())
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(multisig.address).addAuthorizedContract(
                    BOB_PK).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1001"})

        def test03_it_fails_when_caller_votes_twice(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertNotIn(
                BOB_PK, multisig.storage["authorized_contracts"]())
            multisig.addAdmin(
                BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            multisig.addAuthorizedContract(
                BOB_PK).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                multisig.addAuthorizedContract(
                    BOB_PK).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1008"})

    class RemoveAdmin(unittest.TestCase):
        def test01_it_removes_admin(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertNotIn(BOB_PK, multisig.storage["admins"]())
            multisig.addAdmin(BOB_PK).send(**send_conf)
            self.assertIn(BOB_PK, multisig.storage["admins"]())
            multisig.removeAdmin(BOB_PK).send(**send_conf)
            self.assertNotIn(BOB_PK, multisig.storage["admins"]())

        def test02_it_fails_when_caller_not_admin(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertNotIn(
                BOB_PK, multisig.storage["authorized_contracts"]())
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(multisig.address).removeAdmin(
                    ALICE_PK).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1001"})

        def test03_it_fails_when_caller_votes_twice(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertNotIn(BOB_PK, multisig.storage["admins"]())
            multisig.addAdmin(
                BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            multisig.removeAdmin(
                BOB_PK).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                multisig.removeAdmin(
                    BOB_PK).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1008"})

        def test04_it_fails_when_new_admin_list_is_empty(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertEqual([ALICE_PK], multisig.storage["admins"]())
            with self.assertRaises(MichelsonError) as err:
                multisig.removeAdmin(ALICE_PK).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1005"})

        def test05_it_fails_when_new_admin_list_size_is_less_than_threshold(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertNotIn(BOB_PK, multisig.storage["admins"]())
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            self.assertIn(BOB_PK, multisig.storage["admins"]())
            self.assertIn(ALICE_PK, multisig.storage["admins"]())
            self.assertEqual(multisig.storage["threshold"](), 2)
            multisig.removeAdmin(BOB_PK).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(multisig.address).removeAdmin(
                    BOB_PK).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1010"})

    class RemoveAuthorizedContract(unittest.TestCase):
        def test01_it_removes_authorized_contract(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertIn(ALICE_PK, multisig.storage["authorized_contracts"]())
            multisig.removeAuthorizedContract(ALICE_PK).send(**send_conf)
            self.assertNotIn(
                ALICE_PK, multisig.storage["authorized_contracts"]())

        def test02_it_fails_when_caller_not_admin(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertIn(ALICE_PK, multisig.storage["authorized_contracts"]())
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(multisig.address).removeAuthorizedContract(
                    ALICE_PK).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1001"})

        def test03_it_fails_when_caller_votes_twice(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertNotIn(
                BOB_PK, multisig.storage["authorized_contracts"]())
            multisig.addAdmin(
                BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            multisig.removeAuthorizedContract(
                ALICE_PK).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                multisig.removeAuthorizedContract(
                    ALICE_PK).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1008"})

    class SetDuration(unittest.TestCase):
        def test01_it_sets_duration(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertEqual(multisig.storage["duration"](), 3600)
            multisig.setDuration(20).send(**send_conf)
            self.assertEqual(multisig.storage["duration"](), 20)

        def test02_it_fails_when_caller_not_admin(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertEqual(multisig.storage["duration"](), 3600)
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(multisig.address).setDuration(
                    20).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1001"})

        def test03_it_fails_when_caller_votes_twice(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertEqual(multisig.storage["duration"](), 3600)
            multisig.addAdmin(
                BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            multisig.setDuration(
                20).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                multisig.setDuration(
                    20).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1008"})

        def test04_it_fails_when_duration_is_zero(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertEqual(multisig.storage["duration"](), 3600)
            with self.assertRaises(MichelsonError) as err:
                multisig.setDuration(0).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1013"})

    class SetThreshold(unittest.TestCase):
        def test01_it_sets_threshold(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertEqual(multisig.storage["threshold"](), 1)
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            self.assertEqual(multisig.storage["threshold"](), 2)

        def test02_it_fails_when_caller_not_admin(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertEqual(multisig.storage["threshold"](), 1)
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(multisig.address).setThreshold(
                    2).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1001"})

        def test03_it_fails_when_caller_votes_twice(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertEqual(multisig.storage["threshold"](), 1)
            multisig.addAdmin(
                BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            multisig.setThreshold(
                1).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                multisig.setThreshold(
                    1).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1008"})

        def test04_it_fails_when_threshold_is_zero(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertEqual(multisig.storage["threshold"](), 1)
            with self.assertRaises(MichelsonError) as err:
                multisig.setThreshold(0).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1007"})

        def test05_it_fails_when_threshold_is_larger_than_number_of_admins(self):
            multisig = Env().deploy_multisig(MultisigStorage())
            self.assertEqual(multisig.storage["threshold"](), 1)
            self.assertEqual(len(multisig.storage["admins"]()), 1)
            with self.assertRaises(MichelsonError) as err:
                multisig.setThreshold(2).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1006"})

    def test_inner_test_class(self):
        test_classes_to_run = [
            self.AddAdmin,
            self.AddAuthorizedContract,
            self.RemoveAdmin,
            self.RemoveAuthorizedContract,
            self.SetDuration,
            self.SetThreshold,
        ]
        suites_list = []
        for test_class in test_classes_to_run:
            suites_list.append(
                unittest.TestLoader().loadTestsFromTestCase(test_class))

        big_suite = unittest.TestSuite(suites_list)
        unittest.TextTestRunner().run(big_suite)


if __name__ == "__main__":
    unittest.main()
